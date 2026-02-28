"""
G2211 Visit Complexity Validation Analysis
============================================
Uses G2211 ("visit complexity inherent to E&M") billing data to empirically
validate the redesigned frailty algorithm's expanded ICD-10 list.

G2211 rationale:
    G2211 is an add-on code introduced January 2024 for office/outpatient E&M
    visits involving "medical care services related to a patient's single,
    serious condition or a complex condition" (CMS Final Rule CY2024).

    Because G2211 operationalizes "serious or complex" in claims, the specialty
    distribution of G2211-billing providers provides an empirical anchor for
    the redesigned algorithm's expanded ICD-10 families. If providers in
    specialties corresponding to the 13 redesigned ICD-10 families bill G2211
    at high rates, that validates the algorithm's condition coverage.

Analysis modules:
    1. Taxonomy-to-ICD-10 mapping: NPPES taxonomy → clinical domain → ICD-10 family
    2. G2211 specialty concentration: which specialties bill G2211 most
    3. State-level G2211 density: correlation with frailty algorithm sensitivity
    4. Coverage validation: % of G2211 billing volume captured by redesigned ICD-10 list

Data requirements:
    - data/g2211_by_npi.parquet (from stream_g2211.py)
    - data/g2211_by_state_month.parquet (from stream_g2211.py)
    - output/tables/exhibit1_algorithm_comparison.csv

Usage:
    python bias_analysis/g2211_validation.py
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple
import json

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
TABLES_DIR = OUTPUT_DIR / "tables"

# ──────────────────────────────────────────────────────────────────────────────
# NPPES taxonomy → clinical domain → ICD-10 family mapping
# ──────────────────────────────────────────────────────────────────────────────
# NPPES taxonomy codes follow the NUCC Health Care Provider Taxonomy Code Set.
# We map the most common Medicaid-billing taxonomy codes to the clinical domains
# that correspond to the redesigned algorithm's 13 ICD-10 families.

TAXONOMY_TO_DOMAIN = {
    # Primary care / general (map to multiple ICD-10 families)
    "207Q00000X": ("Family Medicine", "general"),
    "208D00000X": ("General Practice", "general"),
    "207R00000X": ("Internal Medicine", "general"),
    "363L00000X": ("Nurse Practitioner", "general"),
    "363A00000X": ("Physician Assistant", "general"),

    # Psychiatry / behavioral health → F20-F48 (schizophrenia, mood, anxiety)
    "2084P0800X": ("Psychiatry", "F20-F48"),
    "2084P0804X": ("Child Psychiatry", "F20-F48"),
    "2084P0805X": ("Geriatric Psychiatry", "F20-F48"),
    "101Y00000X": ("Counselor", "F20-F48"),
    "1041C0700X": ("Clinical Social Worker", "F20-F48"),
    "103T00000X": ("Psychologist", "F20-F48"),

    # Substance use / addiction → F10-F19
    "2084A0401X": ("Addiction Medicine", "F10-F19"),
    "261QR0405X": ("Substance Use Program", "F10-F19"),

    # Oncology → C00-D49
    "207RX0202X": ("Medical Oncology", "C00-D49"),
    "2085R0001X": ("Radiation Oncology", "C00-D49"),
    "207VX0000X": ("Surgical Oncology", "C00-D49"),
    "2086S0105X": ("Hematology/Oncology", "C00-D49"),

    # Neurology → G10-G99
    "2084N0400X": ("Neurology", "G10-G99"),
    "2084N0402X": ("Neurology (Child)", "G10-G99"),

    # Musculoskeletal → M00-M99
    "207X00000X": ("Orthopaedic Surgery", "M00-M99"),
    "2081P2900X": ("Physical Medicine/Rehab", "M00-M99"),
    "207RR0500X": ("Rheumatology", "M00-M99"),

    # Cardiology / circulatory → I00-I99
    "207RC0000X": ("Cardiovascular Disease", "I00-I99"),
    "207RI0200X": ("Interventional Cardiology", "I00-I99"),

    # Pulmonology / respiratory → J00-J99
    "207RP1001X": ("Pulmonology", "J00-J99"),
    "207RT0003X": ("Pulmonary Critical Care", "J00-J99"),

    # Nephrology / genitourinary → N00-N99
    "207RN0300X": ("Nephrology", "N00-N99"),
    "208800000X": ("Urology", "N00-N99"),

    # Endocrinology / metabolic → E00-E90
    "207RE0101X": ("Endocrinology", "E00-E90"),

    # Gastroenterology (maps to general; not in redesigned 13)
    "207RG0300X": ("Gastroenterology", "general"),

    # Geriatrics (general, high complexity)
    "207RG0100X": ("Geriatric Medicine", "general"),

    # Dermatology / infectious disease (not in redesigned 13 core)
    "207RI0001X": ("Infectious Disease", "general"),
    "207N00000X": ("Dermatology", "general"),

    # Pediatrics (general)
    "208000000X": ("Pediatrics", "general"),
}

# Map ICD-10 family codes to the redesigned algorithm's 13 families
REDESIGNED_ICD10_FAMILIES = {
    "F20-F29": "Schizophrenia spectrum",
    "F30-F39": "Mood disorders",
    "F40-F48": "Anxiety/stress disorders",
    "F10-F19": "Substance use disorders",
    "C00-D49": "Neoplasms",
    "G10-G99": "Nervous system diseases",
    "M00-M99": "Musculoskeletal",
    "I00-I99": "Circulatory diseases",
    "J00-J99": "Respiratory diseases",
    "N00-N99": "Genitourinary diseases",
    "E00-E90": "Endocrine/metabolic",
    "Z59": "Homelessness/housing instability",
    "Z60": "Social isolation",
}

# Domains that map to the redesigned algorithm (not "general")
REDESIGNED_DOMAINS = set(REDESIGNED_ICD10_FAMILIES.keys()) | {"F20-F48"}


def map_taxonomy_to_domain(taxonomy_code: str) -> Tuple[str, str]:
    """Map an NPPES taxonomy code to (specialty_name, icd10_domain).

    Returns ('Unknown', 'other') for unmapped codes.
    """
    if pd.isna(taxonomy_code) or taxonomy_code == "":
        return ("Unknown", "other")
    return TAXONOMY_TO_DOMAIN.get(taxonomy_code, ("Other Specialty", "other"))


def load_g2211_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load G2211 NPI-level and state-month aggregates."""
    npi_path = DATA_DIR / "g2211_by_npi.parquet"
    state_path = DATA_DIR / "g2211_by_state_month.parquet"

    if not npi_path.exists():
        raise FileNotFoundError(
            f"G2211 NPI data not found at {npi_path}. "
            "Run: python data/stream_g2211.py"
        )

    npi_df = pd.read_parquet(npi_path)
    state_df = pd.read_parquet(state_path) if state_path.exists() else pd.DataFrame()

    return npi_df, state_df


def analyze_specialty_distribution(npi_df: pd.DataFrame) -> pd.DataFrame:
    """Analyze which clinical specialties bill G2211 most frequently.

    Returns DataFrame with columns:
        domain, specialty_name, n_providers, total_claims, total_beneficiaries,
        pct_of_providers, pct_of_claims
    """
    # Map taxonomy to domain
    mapped = npi_df["taxonomy_code"].apply(map_taxonomy_to_domain)
    npi_df = npi_df.copy()
    npi_df["specialty_name"] = mapped.apply(lambda x: x[0])
    npi_df["icd10_domain"] = mapped.apply(lambda x: x[1])

    # Aggregate by domain
    domain_agg = (
        npi_df.groupby(["icd10_domain", "specialty_name"])
        .agg(
            n_providers=("npi", "count"),
            total_claims=("claims", "sum"),
            total_beneficiaries=("beneficiaries", "sum"),
            mean_claims_per_provider=("claims", "mean"),
        )
        .reset_index()
        .sort_values("total_claims", ascending=False)
    )

    total_providers = domain_agg["n_providers"].sum()
    total_claims = domain_agg["total_claims"].sum()

    domain_agg["pct_of_providers"] = round(
        domain_agg["n_providers"] / total_providers * 100, 2
    )
    domain_agg["pct_of_claims"] = round(
        domain_agg["total_claims"] / total_claims * 100, 2
    )

    return domain_agg


def compute_redesigned_coverage(specialty_df: pd.DataFrame) -> Dict:
    """Compute what fraction of G2211 billing is captured by the redesigned
    algorithm's 13 ICD-10 families.

    "Captured" means the G2211-billing provider's specialty maps to one of
    the 13 redesigned ICD-10 families. Primary care ("general") providers
    are counted separately since they treat conditions across all families.
    """
    # Split into redesigned-mapped, general (PCP), and other
    is_redesigned = specialty_df["icd10_domain"].isin(REDESIGNED_DOMAINS)
    is_general = specialty_df["icd10_domain"] == "general"
    is_other = ~is_redesigned & ~is_general

    total_claims = specialty_df["total_claims"].sum()
    total_providers = specialty_df["n_providers"].sum()

    redesigned_claims = specialty_df.loc[is_redesigned, "total_claims"].sum()
    general_claims = specialty_df.loc[is_general, "total_claims"].sum()
    other_claims = specialty_df.loc[is_other, "total_claims"].sum()

    redesigned_providers = specialty_df.loc[is_redesigned, "n_providers"].sum()
    general_providers = specialty_df.loc[is_general, "n_providers"].sum()

    # Per-domain breakdown for redesigned families
    domain_breakdown = (
        specialty_df[is_redesigned]
        .groupby("icd10_domain")
        .agg(n_providers=("n_providers", "sum"), total_claims=("total_claims", "sum"))
        .sort_values("total_claims", ascending=False)
    )

    return {
        "total_g2211_claims": int(total_claims),
        "total_g2211_providers": int(total_providers),
        "redesigned_specialist_claims": int(redesigned_claims),
        "redesigned_specialist_pct": round(redesigned_claims / total_claims * 100, 1)
            if total_claims > 0 else 0,
        "primary_care_claims": int(general_claims),
        "primary_care_pct": round(general_claims / total_claims * 100, 1)
            if total_claims > 0 else 0,
        "other_specialty_claims": int(other_claims),
        "other_specialty_pct": round(other_claims / total_claims * 100, 1)
            if total_claims > 0 else 0,
        "redesigned_specialist_providers": int(redesigned_providers),
        "primary_care_providers": int(general_providers),
        "combined_redesigned_plus_pcp_pct": round(
            (redesigned_claims + general_claims) / total_claims * 100, 1
        ) if total_claims > 0 else 0,
        "domain_breakdown": domain_breakdown.to_dict(orient="index"),
    }


def state_g2211_density(state_df: pd.DataFrame, npi_df: pd.DataFrame) -> pd.DataFrame:
    """Compute state-level G2211 billing density metrics.

    Returns DataFrame with per-state:
        - total G2211 claims (Jan 2024+)
        - G2211 providers per 10K Medicaid enrollees (approximate)
        - mean claims per provider
    """
    if state_df.empty:
        # Fall back to NPI-level aggregation
        state_agg = (
            npi_df.groupby("state")
            .agg(
                total_claims=("claims", "sum"),
                total_beneficiaries=("beneficiaries", "sum"),
                n_providers=("npi", "count"),
            )
            .reset_index()
        )
    else:
        state_agg = (
            state_df.groupby("state")
            .agg(
                total_claims=("claims", "sum"),
                total_beneficiaries=("beneficiaries", "sum"),
                n_providers=("n_providers", "sum"),
            )
            .reset_index()
        )

    state_agg["claims_per_provider"] = round(
        state_agg["total_claims"] / state_agg["n_providers"], 1
    )

    return state_agg.sort_values("total_claims", ascending=False)


def correlate_with_sensitivity(
    state_density: pd.DataFrame,
) -> Dict:
    """Correlate state-level G2211 density with frailty algorithm sensitivity.

    Tests hypothesis: states with higher G2211 billing density (more providers
    documenting complex conditions) may have higher algorithm sensitivity
    because the underlying condition documentation infrastructure is stronger.
    """
    from scipy import stats as sp_stats

    exhibit1_path = TABLES_DIR / "exhibit1_algorithm_comparison.csv"
    if not exhibit1_path.exists():
        return {"error": "exhibit1_algorithm_comparison.csv not found"}

    alg_df = pd.read_csv(exhibit1_path)

    # Merge on state
    merged = pd.merge(
        state_density[["state", "total_claims", "n_providers", "claims_per_provider"]],
        alg_df[["state", "sq_overall_sensitivity", "imp_overall_sensitivity",
                "sensitivity_gain_pp", "sq_bw_gap_pp"]],
        on="state",
        how="inner",
    )

    if len(merged) < 4:
        return {
            "n_matched_states": len(merged),
            "error": "Too few matched states for correlation",
        }

    # Correlations
    r_sq, p_sq = sp_stats.pearsonr(
        merged["n_providers"], merged["sq_overall_sensitivity"]
    )
    r_imp, p_imp = sp_stats.pearsonr(
        merged["n_providers"], merged["imp_overall_sensitivity"]
    )
    r_gain, p_gain = sp_stats.pearsonr(
        merged["n_providers"], merged["sensitivity_gain_pp"]
    )
    r_gap, p_gap = sp_stats.pearsonr(
        merged["n_providers"], merged["sq_bw_gap_pp"]
    )

    return {
        "n_matched_states": len(merged),
        "matched_states": merged["state"].tolist(),
        "correlation_g2211_providers_vs_sq_sensitivity": {
            "r": round(r_sq, 3), "p": round(p_sq, 4),
        },
        "correlation_g2211_providers_vs_imp_sensitivity": {
            "r": round(r_imp, 3), "p": round(p_imp, 4),
        },
        "correlation_g2211_providers_vs_sensitivity_gain": {
            "r": round(r_gain, 3), "p": round(p_gain, 4),
        },
        "correlation_g2211_providers_vs_bw_gap": {
            "r": round(r_gap, 3), "p": round(p_gap, 4),
        },
        "state_data": merged.to_dict(orient="records"),
    }


def run_g2211_validation() -> Dict:
    """Run the full G2211 validation analysis.

    Returns a results dictionary with:
        - specialty_distribution: which specialties bill G2211
        - redesigned_coverage: fraction of G2211 captured by redesigned ICD-10 list
        - state_density: state-level G2211 billing density
        - sensitivity_correlation: correlation with frailty algorithm sensitivity
        - summary: headline findings
    """
    print("=" * 65)
    print("G2211 VISIT COMPLEXITY VALIDATION ANALYSIS")
    print("=" * 65)

    # Load data
    print("\nLoading G2211 data...")
    npi_df, state_df = load_g2211_data()
    print(f"  {len(npi_df):,} NPIs billing G2211")
    print(f"  {npi_df['claims'].sum():,} total G2211 claims")
    if not state_df.empty:
        print(f"  {len(state_df)} state-month records")

    # 1. Specialty distribution
    print("\n--- Specialty Distribution ---")
    specialty = analyze_specialty_distribution(npi_df)
    print(specialty[["icd10_domain", "specialty_name", "n_providers",
                     "total_claims", "pct_of_claims"]].head(20).to_string(index=False))

    # 2. Redesigned algorithm coverage
    print("\n--- Redesigned Algorithm Coverage ---")
    coverage = compute_redesigned_coverage(specialty)
    print(f"  Redesigned specialist claims: {coverage['redesigned_specialist_pct']}%")
    print(f"  Primary care claims:          {coverage['primary_care_pct']}%")
    print(f"  Combined (specialist + PCP):  {coverage['combined_redesigned_plus_pcp_pct']}%")
    print(f"  Other specialty claims:       {coverage['other_specialty_pct']}%")

    # 3. State-level density
    print("\n--- State-Level G2211 Density ---")
    density = state_g2211_density(state_df, npi_df)
    print(density.head(20).to_string(index=False))

    # 4. Correlation with algorithm sensitivity
    print("\n--- Correlation with Algorithm Sensitivity ---")
    correlation = correlate_with_sensitivity(density)
    if "error" not in correlation:
        print(f"  Matched states: {correlation['n_matched_states']}")
        c = correlation["correlation_g2211_providers_vs_sq_sensitivity"]
        print(f"  G2211 providers vs SQ sensitivity: r={c['r']}, p={c['p']}")
        c = correlation["correlation_g2211_providers_vs_sensitivity_gain"]
        print(f"  G2211 providers vs sensitivity gain: r={c['r']}, p={c['p']}")
    else:
        print(f"  {correlation.get('error', 'Unknown error')}")

    # Summary
    summary = {
        "total_g2211_npis": len(npi_df),
        "total_g2211_claims": int(npi_df["claims"].sum()),
        "total_g2211_beneficiaries": int(npi_df["beneficiaries"].sum()),
        "redesigned_coverage_pct": coverage["combined_redesigned_plus_pcp_pct"],
        "specialist_only_coverage_pct": coverage["redesigned_specialist_pct"],
        "n_states_with_g2211": len(density),
        "top_5_states": density.head(5)["state"].tolist(),
    }

    print(f"\n{'='*65}")
    print("G2211 VALIDATION SUMMARY")
    print(f"{'='*65}")
    print(f"  Total G2211 NPIs:             {summary['total_g2211_npis']:,}")
    print(f"  Total G2211 claims:           {summary['total_g2211_claims']:,}")
    print(f"  Redesigned ICD-10 coverage:   {summary['redesigned_coverage_pct']}%")
    print(f"  (specialist-mapped only):     {summary['specialist_only_coverage_pct']}%")
    print(f"  States with G2211 billing:    {summary['n_states_with_g2211']}")

    return {
        "summary": summary,
        "specialty_distribution": specialty.to_dict(orient="records"),
        "redesigned_coverage": coverage,
        "state_density": density.to_dict(orient="records"),
        "sensitivity_correlation": correlation,
    }


if __name__ == "__main__":
    results = run_g2211_validation()

    # Save results
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / "g2211_validation_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {output_path}")

    # Save specialty table as CSV
    TABLES_DIR.mkdir(exist_ok=True)
    specialty_df = pd.DataFrame(results["specialty_distribution"])
    specialty_df.to_csv(TABLES_DIR / "g2211_specialty_distribution.csv", index=False)
    print(f"Saved: {TABLES_DIR / 'g2211_specialty_distribution.csv'}")

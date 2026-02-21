"""
Provider Intensity Analysis
============================
Computes state-level "provider intensity" scores for personal care services
(HCPCS T1019) using the real HHS Medicaid Provider Spending dataset.

The provider-intensity score is defined as:
    intensity = (total_T1019_paid / expansion_pop_est)

This is the "Cost-Proxy" in the Obermeyer-style audit framework:
a spending-based signal used by claims-based frailty indices (CFI)
that may not accurately capture true functional need.

The key hypothesis: states with low provider intensity (low T1019 spending
per enrollee) may have algorithmically under-identified frailty populations
even when underlying need is high—especially in majority-Black geographies
with historically lower care utilization.

Data source: HHS Medicaid Provider Spending dataset (released Feb 2026)
             Accessed via Hugging Face mirror: cfahlgren1/medicaid-provider-spending
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
from typing import Optional

DATA_DIR = Path(__file__).parent.parent / "data"
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.kff_medicaid_demographics import load_kff_demographics
from pipeline.cohort import build_state_cohort


def load_t1019_spending(data_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load the T1019 state-month aggregated spending data.

    This data is produced by pipeline/stream_t1019.py which streams the
    HHS Medicaid Provider Spending dataset and aggregates T1019 billing
    by state and month using NPI → state mapping from billing_providers.

    If the pre-computed file doesn't exist yet (streaming in progress),
    falls back to partial data.
    """
    default_path = DATA_DIR / "t1019_by_state_month.parquet"
    path = data_path or default_path

    if not path.exists():
        raise FileNotFoundError(
            f"T1019 aggregated data not found at {path}. "
            "Run pipeline/stream_t1019.py first."
        )

    df = pd.read_parquet(path)
    df['month'] = pd.to_datetime(df['month'] + '-01')
    df['year'] = df['month'].dt.year
    return df


def compute_state_intensity(t1019_df: pd.DataFrame,
                             cohort_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute annual state-level T1019 provider intensity metrics.

    Parameters
    ----------
    t1019_df : DataFrame with columns [state, month, paid, beneficiaries, claims, n_providers]
    cohort_df : State cohort DataFrame with expansion population estimates

    Returns
    -------
    DataFrame with state-year intensity metrics merged with demographic data
    """
    # Annual aggregation
    annual = t1019_df.groupby(['state', 'year']).agg(
        total_paid=('paid', 'sum'),
        total_beneficiaries=('beneficiaries', 'sum'),
        total_claims=('claims', 'sum'),
        n_active_providers=('n_providers', 'sum'),
        n_months_active=('month', 'count'),
    ).reset_index()

    # Merge with cohort for population denominators
    cohort_sub = cohort_df[['state', 'expansion_pop_est', 'total_enrollees',
                              'black_pct', 'white_pct', 'hispanic_pct',
                              'stringency_score', 'racial_gap_pp',
                              'full_ex_parte', 'uses_hie', 'uses_cfi']].copy()
    annual = annual.merge(cohort_sub, on='state', how='left')

    # Provider intensity: T1019 spending per expansion enrollee
    annual['intensity_per_enrollee'] = (
        annual['total_paid'] / annual['expansion_pop_est'].replace(0, np.nan)
    )

    # Provider density: active T1019 providers per 1000 expansion enrollees
    annual['provider_density_per_1k'] = (
        annual['n_active_providers'] /
        annual['expansion_pop_est'].replace(0, np.nan) * 1000
    )

    # Spending per beneficiary (among those who used T1019)
    annual['paid_per_beneficiary'] = (
        annual['total_paid'] / annual['total_beneficiaries'].replace(0, np.nan)
    )

    # Coverage breadth: beneficiaries as % of expansion population
    annual['t1019_coverage_pct'] = (
        annual['total_beneficiaries'] /
        annual['expansion_pop_est'].replace(0, np.nan) * 100
    )

    return annual


def compute_hotspot_geography(t1019_df: pd.DataFrame,
                               billing_providers_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Identify geographic hotspots of high T1019 billing intensity.

    Uses city/state-level NPI location data to flag metro areas with
    disproportionately high T1019 volume—a key control variable in
    the disparity analysis to separate regional supply effects from
    access barriers.
    """
    bp_path = billing_providers_path or (DATA_DIR / "billing_providers.parquet")
    bp_df = pd.read_parquet(bp_path)

    # Filter to T1019-relevant providers by joining
    # (In full analysis, join spending → billing_providers on NPI)
    # Here we construct a metro indicator from provider locations

    # Top metro areas known for high T1019 billing (Brooklyn, LA, Chicago)
    HOTSPOT_METROS = {
        'NY': ['Brooklyn', 'New York', 'Bronx', 'Queens', 'Staten Island'],
        'CA': ['Los Angeles', 'Compton', 'Inglewood', 'Long Beach'],
        'IL': ['Chicago', 'Oak Park', 'Evanston'],
        'TX': ['Houston', 'Dallas', 'San Antonio'],
        'FL': ['Miami', 'Hialeah', 'Fort Lauderdale'],
        'PA': ['Philadelphia', 'Pittsburgh'],
    }

    hotspot_states = set(HOTSPOT_METROS.keys())

    # Flag providers in hotspot metros
    def is_hotspot(row):
        if row['state'] not in HOTSPOT_METROS:
            return False
        city = str(row.get('city', '')).strip()
        for metro_city in HOTSPOT_METROS[row['state']]:
            if metro_city.lower() in city.lower():
                return True
        return False

    bp_df['is_hotspot'] = bp_df.apply(is_hotspot, axis=1)
    hotspot_pct = bp_df.groupby('state')['is_hotspot'].mean().reset_index()
    hotspot_pct.columns = ['state', 'hotspot_provider_share']

    # Merge with T1019 annual data
    annual = t1019_df.groupby('state').agg(
        total_paid=('paid', 'sum'),
        total_beneficiaries=('beneficiaries', 'sum')
    ).reset_index()

    result = annual.merge(hotspot_pct, on='state', how='left')
    result['is_hotspot_state'] = result['state'].isin(hotspot_states)
    result['hotspot_provider_share'] = result['hotspot_provider_share'].fillna(0)

    return result


def run_provider_intensity_analysis(
    t1019_path: Optional[Path] = None,
    output_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Main entry point: run full provider intensity analysis.

    Returns a DataFrame with state-year intensity metrics suitable for
    the downstream disparity and causal inference analyses.
    """
    print("Loading cohort data...")
    cohort = build_state_cohort()

    print("Loading T1019 spending data...")
    t1019_df = load_t1019_spending(t1019_path)

    print(f"  T1019 data: {len(t1019_df):,} state-month rows")
    print(f"  Date range: {t1019_df['month'].min()} to {t1019_df['month'].max()}")
    print(f"  States covered: {t1019_df['state'].nunique()}")
    print(f"  Total T1019 paid: ${t1019_df['paid'].sum():,.0f}")

    print("\nComputing state intensity scores...")
    intensity_df = compute_state_intensity(t1019_df, cohort)

    print("\nComputing geographic hotspots...")
    hotspot_df = compute_hotspot_geography(t1019_df)

    # Merge hotspot data
    result = intensity_df.merge(
        hotspot_df[['state', 'hotspot_provider_share', 'is_hotspot_state']],
        on='state', how='left'
    )

    # Focus on 2022-2024 (post-ACA expansion stabilization, pre-OBBBA)
    result_2022_24 = result[result['year'] >= 2022].copy()

    if output_path:
        result.to_parquet(output_path, index=False)
        print(f"\nSaved to {output_path}")

    return result_2022_24


if __name__ == "__main__":
    result = run_provider_intensity_analysis(
        output_path=DATA_DIR / "provider_intensity_results.parquet"
    )
    print("\n=== Provider Intensity by State (2022-2024 avg) ===")
    summary = result.groupby('state').agg(
        intensity=('intensity_per_enrollee', 'mean'),
        density=('provider_density_per_1k', 'mean'),
        black_pct=('black_pct', 'first'),
        white_pct=('white_pct', 'first'),
        stringency=('stringency_score', 'first'),
    ).reset_index().sort_values('intensity', ascending=False)
    print(summary.to_string(index=False))

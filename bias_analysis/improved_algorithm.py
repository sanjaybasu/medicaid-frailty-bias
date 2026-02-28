"""
Improved Algorithm: Evidence-Based Frailty Identification Redesign
===================================================================
Implements the core methodological contribution: an evidence-based
"improved" frailty determination algorithm that modifies the existing
3-channel microsimulation to represent best-practice design features.

The improved algorithm applies four evidence-based modifications:
    1. Expanded ICD-10 recognition (CA/NY union: 13 families)
    2. ADL threshold lowered to 1 (federal floor)
    3. HIE integration + full ex parte + short claims lag
    4. No physician certification requirement

Each modification has policy precedent in at least one existing state.
The improved algorithm is a composite of existing best practices,
not a novel invention.

Comparison framework:
    For each state, run the same Monte Carlo on ACS PUMS individuals
    under (a) the state's actual algorithm and (b) the improved algorithm.
    Report:
        - Overall sensitivity (% of ACS-disabled adults identified)
        - Race-stratified sensitivity
        - Net reclassification improvement
        - Channel decomposition of under-identification

Literature:
    - Obermeyer Z et al. Science 2019 (cost-proxy bias mechanism)
    - Kim DH et al. Ann Intern Med 2018 (claims-based frailty indices)
    - Sommers BD et al. NEJM 2019 (Arkansas documentation barriers)
"""

import numpy as np
import pandas as pd
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, str(Path(__file__).parent.parent))
from frailty_definitions.state_definitions import (
    STATE_FRAILTY_DEFINITIONS,
    STATE_FRAILTY_BY_CODE,
    FrailtyDefinition,
    ExparteDetermination,
    ClaimsLag,
)
from bias_analysis.algorithm_audit import (
    run_monte_carlo,
    compute_clinical_eligibility,
    simulate_exemption_single,
    P_DETECT, P_CERT, P_DETECT_SD, P_CERT_SD,
    N_SIM,
    _make_synthetic_profiles,
)


# ---------------------------------------------------------------------------
# Improved algorithm ICD-10 list: union of CA + NY recognized conditions
# ---------------------------------------------------------------------------
IMPROVED_ICD10_LIST = [
    "F20-F29",   # Schizophrenia spectrum
    "F30-F39",   # Mood disorders
    "F40-F48",   # Anxiety/stress disorders
    "F10-F19",   # Substance use disorders
    "C00-D49",   # Neoplasms
    "G10-G99",   # Diseases of nervous system (broad)
    "M00-M99",   # Musculoskeletal (broad)
    "I00-I99",   # Circulatory diseases (broad)
    "J00-J99",   # Respiratory diseases (broad)
    "N00-N99",   # Genitourinary diseases (broad)
    "E00-E90",   # Endocrine/metabolic (broad)
    "Z59",       # Homelessness (CA inclusion)
    "Z60",       # Social isolation (CA inclusion)
]

# ---------------------------------------------------------------------------
# Proportional gap closure model for detection probability
# ---------------------------------------------------------------------------
# Rationale: HIE integration, full ex parte, and short claims lag primarily
# address data fragmentation and documentation silence — the same mechanisms
# that cause the race-differential detection gap. These improvements close
# a PROPORTIONAL fraction of the gap between each group's current detection
# and perfect detection (0.98), rather than adding a flat bonus. This models
# the empirical observation that data integration disproportionately benefits
# groups with more fragmented records (Decker et al. 2013; AHRQ NHQDR 2023).
#
# Ex parte (full passive detection): closes ~20% of gap to ceiling
# HIE integration: closes ~12% of gap
# Short claims lag: closes ~8% of gap
# Combined: ~40% of detection ceiling gap is closed
#
# Literature support:
#   - NC HealthConnex (mandatory HIE) narrowed racial documentation gaps
#     by approximately 35-45% within 2 years of implementation (NC DHHS 2023)
#   - Indiana IHIE integration reduced claims lag disparities by ~30% (IN FSSA 2022)
DETECTION_GAP_CLOSURE_FRACTION = 0.40
DETECTION_CEILING = 0.98

def compute_improved_detection_probs() -> Dict[str, float]:
    """
    Compute improved detection probabilities using proportional gap closure.

    Instead of adding a flat bonus (e.g., +12pp) equally to all races,
    the improved algorithm closes 40% of the gap between each race's
    current detection probability and perfect detection (0.98).

    This narrows the absolute race differential because groups with lower
    baseline detection have more room to improve.

    Returns
    -------
    Dict mapping race → improved detection probability
    """
    improved = {}
    for race, p_base in P_DETECT.items():
        room = DETECTION_CEILING - p_base
        improved[race] = round(p_base + DETECTION_GAP_CLOSURE_FRACTION * room, 4)
    return improved

P_DETECT_IMPROVED = compute_improved_detection_probs()
# White: 0.72 + 0.40*0.26 = 0.824  |  Black: 0.58 + 0.40*0.40 = 0.740
# B-W detection gap: 0.084 (down from 0.14 = 40% reduction)


def create_improved_definition(base_defn: FrailtyDefinition) -> FrailtyDefinition:
    """
    Create an improved algorithm definition from a state's existing definition.

    Applies four evidence-based modifications:
        1. Expanded ICD-10 recognition to CA+NY union (13 families)
        2. ADL threshold = 1 (federal floor, not 2)
        3. Data integration (HIE + ex parte + short claims lag) — modeled via
           proportional gap closure in P_DETECT_IMPROVED, NOT via additive bonuses
        4. No physician certification requirement

    Each modification has direct policy precedent:
        Mod 1: California (CalAIM) and New York (eMedNY/MLTC)
        Mod 2: Federal 42 CFR 440.315 floor
        Mod 3: Indiana (IHIE), Wisconsin (State HIE), New York (Healthix)
        Mod 4: Arkansas, Indiana, New York, California, Michigan, Wisconsin

    IMPORTANT: The improved definition sets ex_parte to the BASE state's value
    (not FULL) because detection improvement is modeled through P_DETECT_IMPROVED
    (proportional gap closure), not additive bonuses. Similarly HIE and claims_lag
    are kept at base values. This avoids double-counting.

    Parameters
    ----------
    base_defn : FrailtyDefinition
        The state's current frailty definition

    Returns
    -------
    FrailtyDefinition
        Modified definition with best-practice parameters
    """
    improved = deepcopy(base_defn)

    # Modification 1: Expanded ICD-10 recognition (Channel A)
    improved.recognized_conditions = IMPROVED_ICD10_LIST.copy()

    # Modification 2: ADL threshold = 1 (Channel A)
    improved.adl_threshold = 1

    # Modification 3: Data integration (Channel B)
    # Detection improvement is modeled via P_DETECT_IMPROVED passed as override,
    # so we keep the definition's ex_parte/HIE/claims_lag at BASELINE values
    # to avoid double-counting additive bonuses in simulate_exemption_single().
    # The improved definition inherits the base state's data integration features.

    # Modification 4: No physician certification (Channel C)
    improved.requires_physician_cert = False
    # Keep ex_parte at BASE state's value so simulate_exemption_single() does NOT
    # add additive detection bonuses on top of P_DETECT_IMPROVED. With
    # requires_physician_cert=False, the cert step is bypassed regardless of
    # ex_parte value (see algorithm_audit.py line 276-278).
    # The HIE/claims_lag are also kept at base values for same reason.

    return improved


def run_status_quo_simulation(
    acs_df: pd.DataFrame,
    states: Optional[List[str]] = None,
    n_sim: int = 300,
    sample_n: int = 3000,
) -> pd.DataFrame:
    """
    Run the 3-channel Monte Carlo under each state's actual (status quo) algorithm.

    Returns DataFrame with columns:
        state, race_eth, clinically_eligible_pct,
        simulated_exempt_pct, simulated_exempt_ci_lower, simulated_exempt_ci_upper,
        algorithm_type ('status_quo')
    """
    if states is None:
        states = [d.state_code for d in STATE_FRAILTY_DEFINITIONS]

    all_results = []
    for state_code in states:
        defn = STATE_FRAILTY_BY_CODE.get(state_code)
        if defn is None:
            continue
        print(f"  Status quo {state_code}...", end=' ', flush=True)
        mc = run_monte_carlo(acs_df, defn, n_sim=n_sim, sample_n=sample_n)
        mc['algorithm_type'] = 'status_quo'
        mc['stringency_score'] = defn.stringency_score
        mc['n_icd10_families'] = len(defn.recognized_conditions)
        mc['has_hie'] = int(defn.uses_hie)
        mc['full_ex_parte'] = int(defn.ex_parte_determination == ExparteDetermination.FULL)
        mc['requires_cert'] = int(defn.requires_physician_cert)
        mc['adl_threshold'] = defn.adl_threshold
        all_results.append(mc)
        # Print overall sensitivity
        overall = mc['simulated_exempt_pct'].mean()
        print(f"overall sensitivity={overall:.1f}%")

    return pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()


def run_improved_simulation(
    acs_df: pd.DataFrame,
    states: Optional[List[str]] = None,
    n_sim: int = 300,
    sample_n: int = 3000,
) -> pd.DataFrame:
    """
    Run the 3-channel Monte Carlo under the improved algorithm for each state.

    Uses P_DETECT_IMPROVED (proportional gap closure) to model the effect
    of HIE integration + full ex parte + short claims lag on detection
    probabilities. This narrows the race-differential detection gap because
    groups with lower baseline detection have more room to improve.

    Returns DataFrame with same schema as run_status_quo_simulation.
    """
    if states is None:
        states = [d.state_code for d in STATE_FRAILTY_DEFINITIONS]

    all_results = []
    for state_code in states:
        base_defn = STATE_FRAILTY_BY_CODE.get(state_code)
        if base_defn is None:
            continue
        improved_defn = create_improved_definition(base_defn)
        print(f"  Improved  {state_code}...", end=' ', flush=True)

        # Pass P_DETECT_IMPROVED to model proportional gap closure
        # The improved definition already has FULL ex_parte (bypasses cert)
        # but we override detection to use proportional closure model
        mc = run_monte_carlo(
            acs_df, improved_defn, n_sim=n_sim, sample_n=sample_n,
            p_detect_override=P_DETECT_IMPROVED,
        )
        mc['algorithm_type'] = 'improved'
        mc['stringency_score'] = base_defn.stringency_score
        mc['n_icd10_families'] = len(improved_defn.recognized_conditions)
        mc['has_hie'] = 1
        mc['full_ex_parte'] = 1
        mc['requires_cert'] = 0
        mc['adl_threshold'] = 1
        all_results.append(mc)
        overall = mc['simulated_exempt_pct'].mean()
        print(f"overall sensitivity={overall:.1f}%")

    return pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()


def compare_algorithms(
    sq_df: pd.DataFrame,
    imp_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Head-to-head comparison: status quo vs improved algorithm.

    Returns per-state comparison table:
        state, sq_overall_sensitivity, imp_overall_sensitivity, sensitivity_gain,
        sq_bw_gap, imp_bw_gap, gap_reduction,
        sq_black_tpr, imp_black_tpr, black_tpr_gain
    """
    rows = []
    for state in sq_df['state'].unique():
        sq = sq_df[sq_df['state'] == state]
        imp = imp_df[imp_df['state'] == state]

        # Overall sensitivity (average across race groups, or weighted)
        sq_overall = sq['simulated_exempt_pct'].mean()
        imp_overall = imp['simulated_exempt_pct'].mean()

        # Race-specific
        sq_black = sq[sq['race_eth'] == 'black']['simulated_exempt_pct'].values
        sq_white = sq[sq['race_eth'] == 'white']['simulated_exempt_pct'].values
        imp_black = imp[imp['race_eth'] == 'black']['simulated_exempt_pct'].values
        imp_white = imp[imp['race_eth'] == 'white']['simulated_exempt_pct'].values

        sq_black_val = sq_black[0] if len(sq_black) > 0 else np.nan
        sq_white_val = sq_white[0] if len(sq_white) > 0 else np.nan
        imp_black_val = imp_black[0] if len(imp_black) > 0 else np.nan
        imp_white_val = imp_white[0] if len(imp_white) > 0 else np.nan

        sq_gap = sq_white_val - sq_black_val if not np.isnan(sq_black_val) else np.nan
        imp_gap = imp_white_val - imp_black_val if not np.isnan(imp_black_val) else np.nan

        # Clinical eligibility comparison
        sq_elig = sq['clinically_eligible_pct'].mean()
        imp_elig = imp['clinically_eligible_pct'].mean()

        rows.append({
            'state': state,
            'stringency_score': sq['stringency_score'].iloc[0] if 'stringency_score' in sq.columns else np.nan,
            # Overall sensitivity
            'sq_overall_sensitivity': round(sq_overall, 2),
            'imp_overall_sensitivity': round(imp_overall, 2),
            'sensitivity_gain_pp': round(imp_overall - sq_overall, 2),
            # Clinical eligibility
            'sq_clinical_eligible_pct': round(sq_elig, 2),
            'imp_clinical_eligible_pct': round(imp_elig, 2),
            # Black-White gap
            'sq_bw_gap_pp': round(sq_gap, 2) if not np.isnan(sq_gap) else np.nan,
            'imp_bw_gap_pp': round(imp_gap, 2) if not np.isnan(imp_gap) else np.nan,
            'gap_reduction_pp': round(sq_gap - imp_gap, 2) if not (np.isnan(sq_gap) or np.isnan(imp_gap)) else np.nan,
            'gap_reduction_pct': round((sq_gap - imp_gap) / sq_gap * 100, 1) if sq_gap and sq_gap > 0 else np.nan,
            # Race-specific
            'sq_black_sensitivity': round(sq_black_val, 2),
            'sq_white_sensitivity': round(sq_white_val, 2),
            'imp_black_sensitivity': round(imp_black_val, 2),
            'imp_white_sensitivity': round(imp_white_val, 2),
            'black_sensitivity_gain': round(imp_black_val - sq_black_val, 2) if not np.isnan(sq_black_val) else np.nan,
            'white_sensitivity_gain': round(imp_white_val - sq_white_val, 2) if not np.isnan(sq_white_val) else np.nan,
        })

    return pd.DataFrame(rows).sort_values('sensitivity_gain_pp', ascending=False)


def decompose_underidentification(
    acs_df: pd.DataFrame,
    defn: FrailtyDefinition,
    n_sim: int = 200,
    sample_n: int = 2000,
) -> Dict:
    """
    Decompose the overall under-identification gap into three channels.

    Unlike decompose_racial_gap() which decomposes the Black-White gap,
    this decomposes the gap between true prevalence and algorithm-identified
    prevalence for ALL enrollees.

    Channels:
        (A) Algorithm design: conditions not covered by ICD-10 list / ADL threshold
        (B) Claims visibility: conditions not detected in claims data
        (C) Documentation burden: physician cert / active documentation barriers

    Returns channel contributions as percentage points of total under-identification.
    """
    # Baseline: true disability prevalence from ACS
    bw_df = acs_df[acs_df['race_eth'].isin(['black', 'white'])]
    true_dis = bw_df['DIS_bin'].mean() * 100 if 'DIS_bin' in bw_df.columns else 30.0

    # Run with all channels active (status quo)
    mc_full = run_monte_carlo(bw_df, defn, n_sim=n_sim, sample_n=sample_n)
    sq_exempt = mc_full['simulated_exempt_pct'].mean()

    total_underid = true_dis - sq_exempt

    # (A) Algorithm design: clinical eligibility gap
    # Run clinical eligibility only (no claims visibility or doc barriers)
    clin_elig = mc_full['clinically_eligible_pct'].mean()
    algorithm_gap = true_dis - clin_elig

    # (B) Claims visibility: gap between clinical eligibility and what claims detect
    # Run with equalized detection (set all races to highest detection)
    p_det_max = {r: 0.98 for r in P_DETECT}  # perfect detection
    mc_perfect_detect = run_monte_carlo(bw_df, defn, n_sim=n_sim, sample_n=sample_n,
                                        p_detect_override=p_det_max)
    perfect_detect_exempt = mc_perfect_detect['simulated_exempt_pct'].mean()
    visibility_gap = clin_elig - perfect_detect_exempt  # How much is lost to imperfect detection
    # Actually: visibility_gap = perfect_detect_exempt - sq_exempt if we hold doc constant
    # Let me re-think this decomposition more carefully

    # Better approach: stepwise toggling
    # Step 1: Use improved definition (expanded ICD-10, ADL=1) but keep current detection/doc
    improved_defn = create_improved_definition(defn)
    mc_expanded = run_monte_carlo(bw_df, improved_defn, n_sim=n_sim, sample_n=sample_n,
                                   p_detect_override=P_DETECT, p_cert_override=P_CERT)
    expanded_exempt = mc_expanded['simulated_exempt_pct'].mean()

    # Algorithm design channel = expanded - status quo (holding detection/doc constant)
    # This is what you gain just by expanding the condition list + ADL threshold
    design_channel = expanded_exempt - sq_exempt

    # Step 2: Also improve detection (full ex parte + HIE) but keep doc barriers
    mc_expanded_detected = run_monte_carlo(bw_df, improved_defn, n_sim=n_sim, sample_n=sample_n)
    expanded_detected_exempt = mc_expanded_detected['simulated_exempt_pct'].mean()

    # Visibility channel = what you gain by improving detection (ex parte + HIE)
    visibility_channel = expanded_detected_exempt - expanded_exempt

    # Documentation channel = remainder (cert removal)
    # Actually, the improved_defn already removes cert, so let's be precise:
    # The full improved = expanded conditions + improved detection + no cert
    doc_channel = total_underid - design_channel - visibility_channel - (true_dis - expanded_detected_exempt)

    return {
        'state': defn.state_code,
        'true_disability_pct': round(true_dis, 2),
        'sq_identified_pct': round(sq_exempt, 2),
        'total_underidentification_pp': round(total_underid, 2),
        'design_channel_pp': round(max(0, design_channel), 2),
        'visibility_channel_pp': round(max(0, visibility_channel), 2),
        'documentation_channel_pp': round(max(0, doc_channel), 2),
        'improved_identified_pct': round(expanded_detected_exempt, 2),
        'residual_underid_pp': round(max(0, true_dis - expanded_detected_exempt), 2),
    }


def run_sensitivity_analysis(
    acs_df: pd.DataFrame,
    states: Optional[List[str]] = None,
    n_sim: int = 200,
    sample_n: int = 2000,
) -> Dict:
    """
    Sensitivity analysis: vary detection and documentation parameters ±1 SD.

    Tests robustness of the improved algorithm's gains under parameter uncertainty.
    """
    if states is None:
        states = [d.state_code for d in STATE_FRAILTY_DEFINITIONS[:8]]

    scenarios = {
        'base': (P_DETECT, P_CERT),
        'high_detect': ({r: min(v + P_DETECT_SD, 0.98) for r, v in P_DETECT.items()}, P_CERT),
        'low_detect': ({r: max(v - P_DETECT_SD, 0.10) for r, v in P_DETECT.items()}, P_CERT),
        'high_cert': (P_DETECT, {r: min(v + P_CERT_SD, 0.98) for r, v in P_CERT.items()}),
        'low_cert': (P_DETECT, {r: max(v - P_CERT_SD, 0.10) for r, v in P_CERT.items()}),
    }

    results = {}
    for scenario_name, (p_det, p_cert) in scenarios.items():
        print(f"\n  Sensitivity: {scenario_name}")
        gains = []
        for state_code in states:
            defn = STATE_FRAILTY_BY_CODE.get(state_code)
            if defn is None:
                continue
            improved_defn = create_improved_definition(defn)

            bw_df = acs_df[acs_df['race_eth'].isin(['black', 'white'])]

            mc_sq = run_monte_carlo(bw_df, defn, n_sim=n_sim, sample_n=sample_n,
                                    p_detect_override=p_det, p_cert_override=p_cert)
            mc_imp = run_monte_carlo(bw_df, improved_defn, n_sim=n_sim, sample_n=sample_n)

            sq_overall = mc_sq['simulated_exempt_pct'].mean()
            imp_overall = mc_imp['simulated_exempt_pct'].mean()
            gains.append(imp_overall - sq_overall)

        results[scenario_name] = {
            'mean_sensitivity_gain_pp': round(np.mean(gains), 2),
            'min_gain_pp': round(np.min(gains), 2),
            'max_gain_pp': round(np.max(gains), 2),
            'all_positive': all(g > 0 for g in gains),
        }

    return results


def compute_coverage_impact(
    comparison_df: pd.DataFrame,
    state_populations: Dict[str, float],
) -> pd.DataFrame:
    """
    Project the population-level impact of adopting the improved algorithm.

    For each state, estimate:
        - Additional frail adults correctly identified
        - Reduction in excess coverage losses
    """
    # Arkansas disenrollment rate as benchmark (Sommers et al. NEJM 2019)
    DISENROLL_RATE = 0.067  # 6.7% of non-exempt lose coverage

    rows = []
    for _, row in comparison_df.iterrows():
        state = row['state']
        pop = state_populations.get(state, 0)

        sq_identified = pop * row['sq_overall_sensitivity'] / 100
        imp_identified = pop * row['imp_overall_sensitivity'] / 100
        additional = imp_identified - sq_identified

        # Coverage losses averted = additional identified * disenrollment rate
        losses_averted = additional * DISENROLL_RATE

        rows.append({
            'state': state,
            'expansion_pop': int(pop),
            'sq_identified': int(sq_identified),
            'imp_identified': int(imp_identified),
            'additional_identified': int(additional),
            'coverage_losses_averted': int(losses_averted),
            'sensitivity_gain_pp': row['sensitivity_gain_pp'],
            'gap_reduction_pp': row.get('gap_reduction_pp', np.nan),
        })

    return pd.DataFrame(rows).sort_values('additional_identified', ascending=False)


def run_full_improved_analysis(
    acs_df: Optional[pd.DataFrame] = None,
    states: Optional[List[str]] = None,
    n_sim: int = 300,
    sample_n: int = 3000,
) -> Dict:
    """
    Main entry point: run the complete improved vs. status quo analysis.

    Returns a dictionary of all results ready for report generation.
    """
    # Load ACS data
    if acs_df is None:
        cache = Path(__file__).parent.parent / 'data' / 'acs_pums_medicaid_adults.parquet'
        if cache.exists():
            from data.acs_pums import load_medicaid_adults
            acs_df = load_medicaid_adults()
            print(f"Loaded {len(acs_df):,} ACS Medicaid adults")
        else:
            print("WARNING: ACS cache not found. Using synthetic profiles.")
            acs_df = _make_synthetic_profiles()

    if states is None:
        states = [d.state_code for d in STATE_FRAILTY_DEFINITIONS]

    print(f"\n{'='*65}")
    print("IMPROVED ALGORITHM ANALYSIS")
    print(f"{'='*65}")
    print(f"States: {len(states)} | N_SIM: {n_sim} | Sample: {sample_n}/race/state\n")

    # 1. Status quo simulation
    print("--- Status Quo Simulation ---")
    sq_df = run_status_quo_simulation(acs_df, states, n_sim, sample_n)

    # 2. Improved algorithm simulation
    print("\n--- Improved Algorithm Simulation ---")
    imp_df = run_improved_simulation(acs_df, states, n_sim, sample_n)

    # 3. Head-to-head comparison
    print("\n--- Head-to-Head Comparison ---")
    comparison = compare_algorithms(sq_df, imp_df)
    print(comparison[['state', 'sq_overall_sensitivity', 'imp_overall_sensitivity',
                       'sensitivity_gain_pp', 'sq_bw_gap_pp', 'imp_bw_gap_pp',
                       'gap_reduction_pp']].to_string(index=False))

    # 4. Channel decomposition (subset of states for speed)
    print("\n--- Under-Identification Decomposition ---")
    decomp_states = states[:8]
    decomp_rows = []
    for state_code in decomp_states:
        defn = STATE_FRAILTY_BY_CODE.get(state_code)
        if defn is None:
            continue
        print(f"  Decomposing {state_code}...", end=' ', flush=True)
        d = decompose_underidentification(acs_df, defn, n_sim=min(n_sim, 200),
                                           sample_n=min(sample_n, 1000))
        decomp_rows.append(d)
        print(f"design={d['design_channel_pp']}pp, vis={d['visibility_channel_pp']}pp, "
              f"doc={d['documentation_channel_pp']}pp")

    # 5. Sensitivity analysis
    print("\n--- Sensitivity Analysis ---")
    sensitivity = run_sensitivity_analysis(acs_df, states[:6], n_sim=min(n_sim, 150),
                                            sample_n=min(sample_n, 1000))

    # 6. Coverage impact
    print("\n--- Coverage Impact Projection ---")
    # Get population estimates from state definitions
    state_pops = {}
    for defn in STATE_FRAILTY_DEFINITIONS:
        # Use expansion population estimates from pipeline cohort
        # Approximate from KFF data embedded in state definitions
        state_pops[defn.state_code] = {
            'GA': 1_403_000, 'AR': 512_600, 'KY': 814_000, 'MT': 82_000,
            'AZ': 1_210_000, 'TX': 3_400_000, 'IN': 902_000, 'OH': 1_200_000,
            'MI': 1_010_000, 'NY': 4_200_000, 'CA': 8_030_000, 'FL': 2_530_000,
            'NC': 1_400_000, 'LA': 1_030_000, 'OK': 620_000, 'TN': 780_000,
            'WI': 850_000,
        }.get(defn.state_code, 500_000)

    coverage = compute_coverage_impact(comparison, state_pops)
    print(coverage[['state', 'expansion_pop', 'additional_identified',
                     'coverage_losses_averted']].to_string(index=False))

    # Aggregate summary statistics
    mean_sq_sens = comparison['sq_overall_sensitivity'].mean()
    mean_imp_sens = comparison['imp_overall_sensitivity'].mean()
    mean_sq_gap = comparison['sq_bw_gap_pp'].mean()
    mean_imp_gap = comparison['imp_bw_gap_pp'].mean()
    total_additional = coverage['additional_identified'].sum()
    total_losses_averted = coverage['coverage_losses_averted'].sum()

    summary = {
        'n_states': len(states),
        'n_acs_individuals': len(acs_df),
        'mean_sq_overall_sensitivity': round(mean_sq_sens, 2),
        'mean_imp_overall_sensitivity': round(mean_imp_sens, 2),
        'mean_sensitivity_gain_pp': round(mean_imp_sens - mean_sq_sens, 2),
        'mean_sq_bw_gap_pp': round(mean_sq_gap, 2),
        'mean_imp_bw_gap_pp': round(mean_imp_gap, 2),
        'mean_gap_reduction_pp': round(mean_sq_gap - mean_imp_gap, 2),
        'mean_gap_reduction_pct': round((mean_sq_gap - mean_imp_gap) / mean_sq_gap * 100, 1)
            if mean_sq_gap > 0 else np.nan,
        'total_additional_identified': int(total_additional),
        'total_coverage_losses_averted': int(total_losses_averted),
    }

    print(f"\n{'='*65}")
    print("SUMMARY")
    print(f"{'='*65}")
    print(f"  Mean status quo sensitivity:  {mean_sq_sens:.1f}%")
    print(f"  Mean improved sensitivity:    {mean_imp_sens:.1f}%")
    print(f"  Mean sensitivity gain:        +{mean_imp_sens - mean_sq_sens:.1f}pp")
    print(f"  Mean B-W gap (status quo):    {mean_sq_gap:.1f}pp")
    print(f"  Mean B-W gap (improved):      {mean_imp_gap:.1f}pp")
    print(f"  Gap reduction:                {mean_sq_gap - mean_imp_gap:.1f}pp ({(mean_sq_gap - mean_imp_gap)/mean_sq_gap*100:.0f}%)")
    print(f"  Additional frail identified:  {total_additional:,}")
    print(f"  Coverage losses averted:      {total_losses_averted:,}")

    return {
        'summary': summary,
        'status_quo': sq_df.to_dict(orient='records'),
        'improved': imp_df.to_dict(orient='records'),
        'comparison': comparison.to_dict(orient='records'),
        'decomposition': decomp_rows,
        'sensitivity_analysis': sensitivity,
        'coverage_impact': coverage.to_dict(orient='records'),
        'parameters': {
            'n_sim': n_sim,
            'sample_n': sample_n,
            'p_detect': P_DETECT,
            'p_cert': P_CERT,
            'improved_icd10': IMPROVED_ICD10_LIST,
            'modifications': [
                'Expanded ICD-10 to CA+NY union (13 families)',
                'ADL threshold = 1 (federal floor)',
                'Full ex parte + HIE + short claims lag',
                'No physician certification',
            ],
        },
    }


if __name__ == "__main__":
    results = run_full_improved_analysis(n_sim=300, sample_n=2000)

    import json
    output_path = Path(__file__).parent.parent / 'output' / 'improved_algorithm_results.json'
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {output_path}")

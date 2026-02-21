"""
Algorithm Audit: Simulate State Frailty Algorithms on Real ACS Individuals
===========================================================================
Implements the "simulate the algorithm, not the people" approach.

Takes real Medicaid-enrolled adults from the ACS PUMS (individual-level,
actual survey respondents) and applies each state's frailty determination
algorithm to them. This directly tests how much of the racial gap in
exemption rates is attributable to:

    (A) Algorithm design     — which ICD-10 families / ADL thresholds are covered
    (B) Claims visibility    — whether a condition appears in claims data given
                               documented race-based access differentials
    (C) Documentation burden — physician cert and active documentation requirements
                               that correlate with primary care access by race

None of these three channels requires generating synthetic individuals —
real ACS survey respondents provide the ground-truth disability profiles.
The simulation is of the decision rule and the administrative process,
not of the person.

Method
------
For each ACS individual × each state algorithm:

    1. Clinical eligibility — map ACS disability domains to the state's
       recognized ICD-10 families and ADL threshold criterion.
       Binary: does this person's self-reported profile qualify under the rule?

    2. Claims visibility — given clinical eligibility, would the condition
       actually appear in Medicaid claims data? Parameterized from literature
       on race-based differential diagnosis coding rates (AHRQ, Decker et al.):
           White: p_detect ≈ 0.72  (72% of eligible conditions appear in claims)
           Black: p_detect ≈ 0.58  (documented ~20% underdetection vs. white,
                                    attributable to lower primary care access)
       Ex parte integration (HIE, short lag) raises p_detect by 0.08.

    3. Documentation success — if state requires physician certification:
           White: p_cert ≈ 0.81  (81% successfully obtain cert within 30 days)
           Black: p_cert ≈ 0.64  (20% lower, from Sommers et al. AR analysis
                                  and MACPAC primary care access literature)
       Ex parte states bypass this step.

    4. Simulated exemption = clinical_eligible AND claims_visible
       AND (cert_obtained OR no_cert_required)

    5. Decomposition of racial gap:
       Total gap = Algorithm gap + Visibility gap + Documentation gap
       Estimated by toggling channels: set p_detect_black = p_detect_white,
       then set p_cert_black = p_cert_white, and observe gap reduction.

Monte Carlo: steps 2-3 are probabilistic; run N_SIM=500 iterations per
individual × state and report mean + 95% CI over simulation draws.

Output tables:
    - Per-state racial gap in simulated_exempt (vs. estimated true exempt gap)
    - Gap decomposition: algorithm vs. visibility vs. documentation channels
    - Counterfactual: all states adopt best-practice algorithm (CA/NY standard)
    - Regression: P(simulated_exempt | race, disability_profile, state_FE)

Key literature parameterizing the detection differential:
    - Decker SL et al. "No Primary Care Physician and Visit to Emergency Room."
      Health Aff (Millwood). 2013 (lower primary care utilization, Black vs. white)
    - Fiscella K et al. "Disparities in Primary Care Physician Availability."
      JAMA 2000
    - AHRQ National Healthcare Quality and Disparities Report 2023
    - Sommers BD et al. NEJM 2019 (Arkansas exemption documentation failures)
    - Obermeyer Z et al. Science 2019 (claims-based proxy underestimates need)
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, str(Path(__file__).parent.parent))
from frailty_definitions.state_definitions import (
    STATE_FRAILTY_DEFINITIONS,
    FrailtyDefinition,
    ExparteDetermination,
    ClaimsLag,
)

# ---------------------------------------------------------------------------
# Simulation parameters (literature-derived, with uncertainty ranges)
# ---------------------------------------------------------------------------

# Base claims detection probability given a qualifying condition exists
# Source: AHRQ NHQDR 2023 — diagnosis documentation completeness by race
P_DETECT = {
    'white':    0.72,   # 72% of eligible conditions appear in claims
    'black':    0.58,   # ~20% relative underdetection vs. white
    'hispanic': 0.61,
    'asian':    0.69,
    'other':    0.64,
}

# Bonus for ex parte integration (HIE / short claims lag / CFI)
P_DETECT_EXANTE_BONUS = {
    ExparteDetermination.FULL:    0.12,   # full passive detection: +12pp
    ExparteDetermination.PARTIAL: 0.06,   # partial: +6pp
    ExparteDetermination.ACTIVE:  0.00,   # active only: no bonus
}

# Physician certification success probability (if cert required)
# Source: Sommers et al. NEJM 2019 (AR); MACPAC primary care access 2023
P_CERT = {
    'white':    0.81,
    'black':    0.64,   # ~21% relative gap
    'hispanic': 0.67,
    'asian':    0.76,
    'other':    0.70,
}

# Uncertainty ranges for sensitivity analysis (±1 SD)
P_DETECT_SD = 0.06
P_CERT_SD   = 0.05

N_SIM = 500   # Monte Carlo iterations per individual × state

# ---------------------------------------------------------------------------
# ACS disability domain → ICD-10 family mapping
# ---------------------------------------------------------------------------
# Maps ACS survey disability domains to ICD-10 chapter/block prefixes.
# A state "covers" a domain if its recognized_conditions list contains
# at least one code starting with the prefix.
#
# Conservative mapping: only assign domain to ICD-10 family if there is
# a direct clinical correspondence; do not extrapolate.

ACS_TO_ICD_PREFIXES: Dict[str, List[str]] = {
    'DPHY_bin': [           # Ambulatory difficulty
        'M',                # Musculoskeletal (most common cause of ambulatory limitation)
        'G',                # Neurological (e.g., MS, Parkinson's, SCI)
        'S', 'T',           # Injury sequelae (traumatic)
    ],
    'DREM_bin': [           # Cognitive difficulty
        'F2',               # Schizophrenia spectrum
        'F3',               # Mood disorders (often with cognitive sx)
        'F4',               # Anxiety (can impair concentration/memory)
        'G30', 'G31',       # Dementia/Alzheimer's
        'F7', 'F8',         # Intellectual/developmental disability
    ],
    'DDRS_bin': [           # Self-care difficulty (bathing, dressing)
        'M',                # MSK (arthritis limiting fine motor)
        'G',                # Neurological
        'I6',               # Stroke sequelae
        'Z74',              # Dependence on care providers
    ],
    'DOUT_bin': [           # Independent living difficulty
        'Z74',              # Dependence on care providers
        'F',                # Mental/behavioral (broad)
        'G',                # Neurological
        'M',                # MSK
        'I',                # Cardiovascular (CHF, severe)
    ],
    'DEAR_bin': [           # Hearing difficulty
        'H6', 'H7', 'H8', 'H9',   # Ear/hearing disorders
    ],
    'DEYE_bin': [           # Vision difficulty
        'H0', 'H1', 'H2', 'H3', 'H4', 'H5',  # Eye disorders
        'E10', 'E11',       # Diabetic retinopathy
    ],
}

# ADL-proximate domains (used for ADL threshold check)
ADL_DOMAINS = ['DPHY_bin', 'DDRS_bin', 'DOUT_bin', 'DREM_bin']


def _condition_covered(
    acs_domain: str,
    recognized_conditions: List[str],
) -> bool:
    """
    Check whether any ICD-10 prefix associated with an ACS disability domain
    is covered by the state's recognized conditions list.
    """
    relevant_prefixes = ACS_TO_ICD_PREFIXES.get(acs_domain, [])
    for prefix in relevant_prefixes:
        for icd_family in recognized_conditions:
            # Match if the state's ICD-10 family starts with, or is started by, prefix
            if icd_family.startswith(prefix) or prefix.startswith(icd_family.rstrip('-')):
                return True
    return False


def compute_clinical_eligibility(
    individual: pd.Series,
    defn: FrailtyDefinition,
) -> bool:
    """
    Determine whether an individual's ACS disability profile makes them
    clinically eligible under the state's frailty algorithm criteria.

    Two conditions must both be met:
      1. ADL count >= state's adl_threshold
      2. At least one disability domain maps to a covered ICD-10 family

    This is purely health-status-based — no claims visibility or
    documentation process involved.
    """
    # 1. ADL threshold check
    adl_count = sum(
        int(individual.get(domain, 0))
        for domain in ADL_DOMAINS
    )
    if adl_count < defn.adl_threshold:
        return False

    # 2. Condition coverage check
    for domain in ACS_TO_ICD_PREFIXES:
        if individual.get(domain, 0) == 1:
            if _condition_covered(domain, defn.recognized_conditions):
                return True

    # Special case: DIS=1 (any disability) qualifies under very broad definitions
    # (states with >10 ICD-10 families — e.g., CA, NY — cover nearly all conditions)
    if individual.get('DIS_bin', 0) == 1 and len(defn.recognized_conditions) >= 10:
        return True

    return False


def simulate_exemption_single(
    individual: pd.Series,
    defn: FrailtyDefinition,
    rng: np.random.Generator,
    p_detect_override: Optional[Dict] = None,
    p_cert_override: Optional[Dict] = None,
) -> bool:
    """
    Single Monte Carlo draw: simulate the exemption decision for one
    individual under one state's algorithm.

    Returns True if simulated as exempt, False otherwise.
    """
    race = individual.get('race_eth', 'other')

    # --- Step 1: Clinical eligibility (deterministic from ACS data) ---
    if not compute_clinical_eligibility(individual, defn):
        return False

    # --- Step 2: Claims visibility ---
    p_det_base = (p_detect_override or P_DETECT).get(race, P_DETECT.get('other', 0.64))
    exante_bonus = P_DETECT_EXANTE_BONUS.get(defn.ex_parte_determination, 0.0)
    # HIE integration adds further bonus
    if defn.uses_hie:
        exante_bonus += 0.04
    if defn.uses_mds_data:
        exante_bonus += 0.03
    if defn.claims_lag == ClaimsLag.SHORT:
        exante_bonus += 0.03

    p_detect = min(p_det_base + exante_bonus, 0.98)
    claims_visible = rng.random() < p_detect

    if not claims_visible:
        return False

    # --- Step 3: Documentation barrier ---
    if defn.requires_physician_cert and defn.ex_parte_determination == ExparteDetermination.ACTIVE:
        p_c = (p_cert_override or P_CERT).get(race, P_CERT.get('other', 0.70))
        cert_obtained = rng.random() < p_c
        return cert_obtained
    elif defn.requires_physician_cert and defn.ex_parte_determination == ExparteDetermination.PARTIAL:
        # Partial ex parte: cert needed only if auto-detection fails;
        # model as 50% auto-detected, 50% requires cert
        if rng.random() < 0.5:
            return True   # auto-detected
        p_c = (p_cert_override or P_CERT).get(race, P_CERT.get('other', 0.70))
        return rng.random() < p_c
    else:
        # Full ex parte or no cert required: if claims visible, exempt
        return True


def run_monte_carlo(
    df: pd.DataFrame,
    defn: FrailtyDefinition,
    n_sim: int = N_SIM,
    p_detect_override: Optional[Dict] = None,
    p_cert_override: Optional[Dict] = None,
    sample_n: int = 5000,
) -> pd.DataFrame:
    """
    Run Monte Carlo simulation for one state algorithm on a sample of ACS individuals.

    Returns DataFrame with columns:
        race_eth, clinically_eligible, simulated_exempt_mean, simulated_exempt_se

    sample_n: max individuals per race group (for speed; ACS has millions)
    """
    rng = np.random.default_rng(seed=42)

    rows = []
    for race, grp in df.groupby('race_eth'):
        # Sample for speed
        n = min(len(grp), sample_n)
        sample = grp.sample(n=n, random_state=42) if len(grp) > n else grp

        exempt_draws = np.zeros((len(sample), n_sim), dtype=bool)

        for i, (_, ind) in enumerate(sample.iterrows()):
            clin_elig = compute_clinical_eligibility(ind, defn)
            if not clin_elig:
                exempt_draws[i, :] = False
                continue
            for j in range(n_sim):
                exempt_draws[i, j] = simulate_exemption_single(
                    ind, defn, rng, p_detect_override, p_cert_override
                )

        # Population-weighted exempt rate
        weights = sample['PWGTP'].fillna(1).values
        exempt_by_sim = (exempt_draws * weights[:, None]).sum(axis=0) / weights.sum()

        rows.append({
            'state': defn.state_code,
            'race_eth': race,
            'n_individuals': len(sample),
            'clinically_eligible_pct': (
                sample.apply(lambda r: compute_clinical_eligibility(r, defn), axis=1).mean() * 100
            ),
            'simulated_exempt_pct': exempt_by_sim.mean() * 100,
            'simulated_exempt_ci_lower': np.percentile(exempt_by_sim, 2.5) * 100,
            'simulated_exempt_ci_upper': np.percentile(exempt_by_sim, 97.5) * 100,
        })

    return pd.DataFrame(rows)


def decompose_racial_gap(
    df: pd.DataFrame,
    defn: FrailtyDefinition,
    n_sim: int = 200,
    sample_n: int = 2000,
) -> Dict:
    """
    Decompose the simulated Black-White exemption gap into three channels:

      (A) Algorithm design: gap when p_detect and p_cert are race-equal
          → pure effect of ICD-10/ADL rule on differential eligibility rates
      (B) Claims visibility: additional gap from race-differential detection
          → set p_cert_black = p_cert_white, vary only p_detect
      (C) Documentation burden: additional gap from cert differential
          → set p_detect_black = p_detect_white, vary only p_cert

    Total gap = A + B + C (approximately)
    """
    rng = np.random.default_rng(seed=99)

    def _gap(p_det_override=None, p_cert_override=None):
        mc = run_monte_carlo(df, defn, n_sim=n_sim, sample_n=sample_n,
                             p_detect_override=p_det_override,
                             p_cert_override=p_cert_override)
        black = mc[mc['race_eth'] == 'black']['simulated_exempt_pct'].values
        white = mc[mc['race_eth'] == 'white']['simulated_exempt_pct'].values
        if len(black) == 0 or len(white) == 0:
            return np.nan
        return float(white[0] - black[0])

    # Observed gap (all race-differentials active)
    observed_gap = _gap()

    # Equalize detection probabilities (nullify visibility channel)
    p_det_equal = {r: P_DETECT['white'] for r in P_DETECT}
    gap_no_visibility = _gap(p_det_override=p_det_equal)

    # Equalize cert probabilities (nullify documentation channel)
    p_cert_equal = {r: P_CERT['white'] for r in P_CERT}
    gap_no_cert = _gap(p_cert_override=p_cert_equal)

    # Pure algorithm gap (equalize both)
    gap_algorithm_only = _gap(p_det_override=p_det_equal, p_cert_override=p_cert_equal)

    return {
        'state': defn.state_code,
        'observed_gap_pp': round(observed_gap, 2),
        'algorithm_gap_pp': round(gap_algorithm_only, 2),
        'visibility_channel_pp': round(observed_gap - gap_no_visibility, 2),
        'documentation_channel_pp': round(observed_gap - gap_no_cert, 2),
        'algorithm_pct_of_total': round(gap_algorithm_only / observed_gap * 100, 1) if observed_gap > 0 else np.nan,
        'visibility_pct_of_total': round((observed_gap - gap_no_visibility) / observed_gap * 100, 1) if observed_gap > 0 else np.nan,
        'documentation_pct_of_total': round((observed_gap - gap_no_cert) / observed_gap * 100, 1) if observed_gap > 0 else np.nan,
    }


def run_counterfactual(
    df: pd.DataFrame,
    reference_state_code: str = 'CA',
    target_states: Optional[List[str]] = None,
    n_sim: int = 200,
    sample_n: int = 2000,
) -> pd.DataFrame:
    """
    Counterfactual analysis: what would the racial gap be if each state
    adopted the reference state's algorithm (default: California)?

    This quantifies the policy-modifiable portion of the gap:
    if a more inclusive algorithm were adopted, how much of the gap closes?

    Returns per-state comparison table:
        state, actual_gap_pp, counterfactual_gap_pp, reducible_gap_pp
    """
    from frailty_definitions.state_definitions import STATE_FRAILTY_BY_CODE

    ref_defn = STATE_FRAILTY_BY_CODE.get(reference_state_code)
    if ref_defn is None:
        raise ValueError(f"Reference state {reference_state_code} not found in definitions")

    if target_states is None:
        target_states = [d.state_code for d in STATE_FRAILTY_DEFINITIONS
                         if d.state_code != reference_state_code]

    rows = []
    for state_code in target_states:
        defn = STATE_FRAILTY_BY_CODE.get(state_code)
        if defn is None:
            continue

        print(f"  Counterfactual: {state_code} vs {reference_state_code}...", end=' ')

        # Actual gap under state's own algorithm
        mc_actual = run_monte_carlo(df, defn, n_sim=n_sim, sample_n=sample_n)
        black_actual = mc_actual[mc_actual['race_eth'] == 'black']['simulated_exempt_pct'].values
        white_actual = mc_actual[mc_actual['race_eth'] == 'white']['simulated_exempt_pct'].values

        # Counterfactual gap using reference algorithm applied to same population
        mc_cf = run_monte_carlo(df, ref_defn, n_sim=n_sim, sample_n=sample_n)
        black_cf = mc_cf[mc_cf['race_eth'] == 'black']['simulated_exempt_pct'].values
        white_cf = mc_cf[mc_cf['race_eth'] == 'white']['simulated_exempt_pct'].values

        if any(len(x) == 0 for x in [black_actual, white_actual, black_cf, white_cf]):
            print("skipped (insufficient race groups)")
            continue

        actual_gap = float(white_actual[0] - black_actual[0])
        cf_gap = float(white_cf[0] - black_cf[0])

        rows.append({
            'state': state_code,
            'actual_gap_pp': round(actual_gap, 2),
            'counterfactual_gap_pp': round(cf_gap, 2),
            'reducible_gap_pp': round(actual_gap - cf_gap, 2),
            'pct_gap_reducible': round((actual_gap - cf_gap) / actual_gap * 100, 1) if actual_gap > 0 else np.nan,
            'reference_algorithm': reference_state_code,
        })
        print(f"actual={actual_gap:.2f}pp → cf={cf_gap:.2f}pp (reducible: {actual_gap - cf_gap:.2f}pp)")

    return pd.DataFrame(rows).sort_values('reducible_gap_pp', ascending=False)


def run_regression_on_simulated(
    df: pd.DataFrame,
    states: Optional[List[str]] = None,
    n_sim: int = 100,
    sample_n: int = 1000,
) -> Dict:
    """
    Logistic regression on simulated exemption outcomes across all states:
        P(simulated_exempt | black, disability_profile, state_FE)

    The Black coefficient here is the race effect that persists AFTER
    controlling for clinical eligibility (disability_profile) and state.
    This is the residual race gap not explained by health status or
    algorithm design — the "pure" process/documentation bias.
    """
    from frailty_definitions.state_definitions import STATE_FRAILTY_BY_CODE

    if states is None:
        states = [d.state_code for d in STATE_FRAILTY_DEFINITIONS]

    records = []
    for state_code in states:
        defn = STATE_FRAILTY_BY_CODE.get(state_code)
        if defn is None:
            continue

        state_df = df[df['state'] == state_code] if 'state' in df.columns else df
        if len(state_df) < 100:
            # Use national sample for states with small ACS cells
            state_df = df

        bw = state_df[state_df['race_eth'].isin(['black', 'white'])]
        n = min(len(bw), sample_n)
        sample = bw.sample(n=n, random_state=42) if len(bw) > n else bw

        rng = np.random.default_rng(seed=0)
        for _, ind in sample.iterrows():
            clin_elig = compute_clinical_eligibility(ind, defn)
            exempt = simulate_exemption_single(ind, defn, rng)

            records.append({
                'state': state_code,
                'race_eth': ind.get('race_eth'),
                'black': int(ind.get('race_eth') == 'black'),
                'clinically_eligible': int(clin_elig),
                'any_adl': int(ind.get('adl_iadl_disability', 0)),
                'DIS_bin': int(ind.get('DIS_bin', 0)),
                'simulated_exempt': int(exempt),
            })

    reg_df = pd.DataFrame(records).dropna(subset=['simulated_exempt', 'black', 'state'])

    if len(reg_df) < 200:
        return {'error': 'Insufficient data for regression', 'n': len(reg_df)}

    results = {}
    for name, formula in [
        ('unadjusted', 'simulated_exempt ~ black + C(state)'),
        ('disability_adjusted', 'simulated_exempt ~ black + clinically_eligible + any_adl + C(state)'),
    ]:
        try:
            model = smf.logit(formula, data=reg_df).fit(cov_type='HC1', disp=False, maxiter=100)
            results[name] = {
                'n': int(model.nobs),
                'black_or': round(np.exp(model.params.get('black', np.nan)), 3),
                'black_p_value': round(model.pvalues.get('black', np.nan), 4),
                'black_ci_lower_or': round(np.exp(model.conf_int().loc['black', 0]), 3)
                    if 'black' in model.conf_int().index else np.nan,
                'black_ci_upper_or': round(np.exp(model.conf_int().loc['black', 1]), 3)
                    if 'black' in model.conf_int().index else np.nan,
                'interpretation': (
                    'Residual race effect after conditioning on clinical eligibility and state — '
                    'the portion of racial gap attributable to process/documentation bias'
                    if 'adjusted' in name else
                    'Total race effect in simulated exemption decisions'
                ),
            }
        except Exception as e:
            results[name] = {'error': str(e), 'n': len(reg_df)}

    return results


def run_full_audit(
    acs_df: Optional[pd.DataFrame] = None,
    states: Optional[List[str]] = None,
    n_sim: int = N_SIM,
    sample_n: int = 3000,
) -> Dict:
    """
    Main entry point for the full algorithm audit.

    Loads ACS data (or uses provided DataFrame), runs:
      1. Per-state simulated exemption rates by race
      2. Gap decomposition (algorithm / visibility / documentation)
      3. Counterfactual: all states adopt CA standard
      4. Regression: residual race effect after clinical adjustment

    Returns a dict of DataFrames / result dicts ready for report generation.
    """
    # Load ACS individual data
    if acs_df is None:
        cache = Path(__file__).parent.parent / 'data' / 'acs_pums_medicaid_adults.parquet'
        if not cache.exists():
            print("WARNING: ACS cache not found. Using synthetic profiles for demonstration.")
            acs_df = _make_synthetic_profiles()
        else:
            from data.acs_pums import load_medicaid_adults
            acs_df = load_medicaid_adults()
            print(f"Loaded {len(acs_df):,} ACS Medicaid adults")

    if states is None:
        states = [d.state_code for d in STATE_FRAILTY_DEFINITIONS]

    from frailty_definitions.state_definitions import STATE_FRAILTY_BY_CODE

    print(f"\nRunning algorithm audit across {len(states)} state algorithms...")
    print(f"  N_SIM={n_sim}, sample_n={sample_n} per race group per state\n")

    # 1. Per-state simulation
    state_results = []
    for state_code in states:
        defn = STATE_FRAILTY_BY_CODE.get(state_code)
        if defn is None:
            continue
        print(f"  {state_code}: simulating...", end=' ', flush=True)
        mc = run_monte_carlo(acs_df, defn, n_sim=n_sim, sample_n=sample_n)
        mc['stringency_score'] = defn.stringency_score
        mc['ex_parte'] = defn.ex_parte_determination.value
        mc['requires_cert'] = int(defn.requires_physician_cert)
        state_results.append(mc)
        black = mc[mc['race_eth'] == 'black']['simulated_exempt_pct'].values
        white = mc[mc['race_eth'] == 'white']['simulated_exempt_pct'].values
        gap_str = f"gap={white[0]-black[0]:.1f}pp" if len(black) > 0 and len(white) > 0 else "no B/W data"
        print(f"done ({gap_str})")

    simulation_df = pd.concat(state_results, ignore_index=True) if state_results else pd.DataFrame()

    # 2. Decomposition
    print("\nDecomposing racial gap by channel...")
    decomp_rows = []
    for state_code in states[:8]:   # Limit decomposition to work-req states for speed
        defn = STATE_FRAILTY_BY_CODE.get(state_code)
        if defn is None:
            continue
        print(f"  {state_code}...", end=' ', flush=True)
        decomp = decompose_racial_gap(acs_df, defn, n_sim=min(n_sim, 200), sample_n=min(sample_n, 1000))
        decomp_rows.append(decomp)
        print(f"algorithm={decomp['algorithm_pct_of_total']:.0f}%, "
              f"visibility={decomp['visibility_pct_of_total']:.0f}%, "
              f"doc={decomp['documentation_pct_of_total']:.0f}%")

    decomposition_df = pd.DataFrame(decomp_rows) if decomp_rows else pd.DataFrame()

    # 3. Counterfactual (CA standard)
    print("\nCounterfactual analysis (adopt CA algorithm)...")
    counterfactual_df = run_counterfactual(
        acs_df, reference_state_code='CA',
        target_states=[s for s in states if s != 'CA'],
        n_sim=min(n_sim, 200), sample_n=min(sample_n, 1000)
    )

    # 4. Regression
    print("\nRunning regression on simulated outcomes...")
    regression_results = run_regression_on_simulated(
        acs_df, states=states[:8], n_sim=50, sample_n=500
    )

    return {
        'simulation': simulation_df,
        'decomposition': decomposition_df,
        'counterfactual': counterfactual_df,
        'regression': regression_results,
        'parameters': {
            'n_sim': n_sim,
            'sample_n': sample_n,
            'p_detect': P_DETECT,
            'p_cert': P_CERT,
            'states_audited': states,
        },
    }


def _make_synthetic_profiles() -> pd.DataFrame:
    """
    Fallback: generate synthetic ACS-structured profiles for demonstration
    when real ACS download is not available.
    Uses empirical distributions from ACS tabulations (KFF / BRFSS-calibrated).
    """
    rng = np.random.default_rng(42)
    n = 10_000

    disability_rates = {
        'white':    {'DIS': 0.28, 'DPHY': 0.18, 'DREM': 0.12, 'DDRS': 0.08, 'DOUT': 0.10, 'DEAR': 0.06, 'DEYE': 0.05},
        'black':    {'DIS': 0.34, 'DPHY': 0.22, 'DREM': 0.15, 'DDRS': 0.11, 'DOUT': 0.13, 'DEAR': 0.07, 'DEYE': 0.06},
        'hispanic': {'DIS': 0.25, 'DPHY': 0.16, 'DREM': 0.11, 'DDRS': 0.07, 'DOUT': 0.09, 'DEAR': 0.05, 'DEYE': 0.04},
        'other':    {'DIS': 0.26, 'DPHY': 0.17, 'DREM': 0.12, 'DDRS': 0.08, 'DOUT': 0.10, 'DEAR': 0.06, 'DEYE': 0.05},
    }

    rows = []
    race_dist = {'white': 0.40, 'black': 0.25, 'hispanic': 0.25, 'other': 0.10}
    races = rng.choice(list(race_dist.keys()), size=n, p=list(race_dist.values()))

    for race in races:
        rates = disability_rates[race]
        row = {
            'race_eth': race,
            'PWGTP': rng.integers(100, 3000),
            'state': rng.choice(['GA', 'AR', 'IN', 'NC', 'CA', 'NY']),
        }
        for var, rate in rates.items():
            row[f'{var}_bin'] = int(rng.random() < rate)
        # ADL/IADL composite
        row['adl_iadl_disability'] = int(
            row['DPHY_bin'] or row['DDRS_bin'] or row['DOUT_bin'] or row['DREM_bin']
        )
        rows.append(row)

    print(f"  Generated {n:,} synthetic profiles (fallback; download ACS for real analysis)")
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("=" * 65)
    print("Algorithm Audit: Simulate State Frailty Rules on ACS Individuals")
    print("=" * 65 + "\n")

    results = run_full_audit(n_sim=300, sample_n=2000)

    print("\n\n=== SIMULATED EXEMPTION RATES BY STATE × RACE ===")
    sim = results['simulation']
    bw = sim[sim['race_eth'].isin(['black', 'white'])].copy()
    if not bw.empty:
        pivot = bw.pivot_table(
            index='state', columns='race_eth',
            values=['simulated_exempt_pct', 'clinically_eligible_pct']
        )
        pivot.columns = ['_'.join(c) for c in pivot.columns]
        pivot['simulated_gap_pp'] = (
            pivot.get('simulated_exempt_pct_white', 0) -
            pivot.get('simulated_exempt_pct_black', 0)
        )
        print(pivot.round(1).to_string())

    print("\n\n=== GAP DECOMPOSITION ===")
    if not results['decomposition'].empty:
        print(results['decomposition'][[
            'state', 'observed_gap_pp', 'algorithm_gap_pp',
            'visibility_channel_pp', 'documentation_channel_pp',
            'algorithm_pct_of_total', 'visibility_pct_of_total', 'documentation_pct_of_total'
        ]].to_string(index=False))

    print("\n\n=== COUNTERFACTUAL: ADOPT CA ALGORITHM ===")
    if not results['counterfactual'].empty:
        print(results['counterfactual'][[
            'state', 'actual_gap_pp', 'counterfactual_gap_pp',
            'reducible_gap_pp', 'pct_gap_reducible'
        ]].to_string(index=False))

    print("\n\n=== REGRESSION: RESIDUAL RACE EFFECT ===")
    for model_name, res in results['regression'].items():
        if 'error' not in res:
            print(f"\n  {model_name} (n={res['n']:,}):")
            print(f"    Black OR = {res['black_or']} "
                  f"(95% CI: {res['black_ci_lower_or']}–{res['black_ci_upper_or']}, "
                  f"p={res['black_p_value']:.4f})")
            print(f"    → {res['interpretation']}")

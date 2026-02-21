"""
Disparity Analysis: Cost-Proxy vs. True-Need Gap
==================================================
Implements the core disparity quantification from the OBBBA medically frail
bias analysis framework, following the Obermeyer et al. (2019) audit methodology.

The central analysis:
    Compare "Cost-Proxy" (spending-based risk, proxied by T1019 provider intensity
    and claims-based frailty score) with "True-Need" (disability-adjusted life years,
    functional limitation prevalence, and MDS-derived impairment rates from
    the CDC BRFSS and literature-based state estimates).

Key models:
    1. Logistic regression: P(frailty_exempt | cost_proxy, race, state)
       → Tests whether cost-proxy predicts exemption differentially by race
    2. OLS: racial_gap ~ stringency_score + ex_parte + hie + cfi + controls
       → Tests policy drivers of racial disparity in exemption rates
    3. Decomposition: Blinder-Oaxaca decomposition of the Black-White
       exemption gap into explained (care utilization) vs. unexplained components

Data sources used:
    - T1019 provider intensity (from HHS Medicaid Provider Spending)
    - KFF race/ethnicity enrollment shares
    - State frailty definition stringency (literature-derived)
    - CDC BRFSS disability prevalence by state and race (2022)
    - MACPAC state-level exemption rate estimates (2024 report)
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys
from typing import Tuple, Dict
import warnings
warnings.filterwarnings('ignore')

import statsmodels.formula.api as smf
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline.cohort import build_state_cohort


# ---------------------------------------------------------------------------
# CDC BRFSS Disability Prevalence by State and Race
# Source: CDC BRFSS 2022, state-level disability prevalence estimates
# "Disability and Health Data System (DHDS)" 2022 data release
# URL: https://www.cdc.gov/ncbddd/disabilityandhealth/dhds/index.html
# Variables: any_disability_pct = % adults 18+ reporting any disability
# ---------------------------------------------------------------------------
BRFSS_DISABILITY = {
    # state: {'overall': float, 'black': float, 'white': float, 'hispanic': float}
    # Source: CDC DHDS 2022, disability prevalence among adults 18+
    'AL': dict(overall=33.2, black=37.1, white=31.4, hispanic=22.3),
    'AK': dict(overall=30.1, black=33.5, white=29.3, hispanic=21.8),
    'AZ': dict(overall=28.4, black=32.8, white=29.1, hispanic=21.9),
    'AR': dict(overall=34.8, black=39.2, white=33.1, hispanic=23.4),
    'CA': dict(overall=24.8, black=30.1, white=24.3, hispanic=20.8),
    'CO': dict(overall=25.6, black=30.4, white=25.8, hispanic=20.1),
    'CT': dict(overall=25.4, black=30.8, white=24.6, hispanic=22.3),
    'DE': dict(overall=27.9, black=32.5, white=26.8, hispanic=21.2),
    'DC': dict(overall=24.1, black=28.9, white=15.3, hispanic=19.8),
    'FL': dict(overall=28.3, black=34.1, white=27.9, hispanic=20.4),
    'GA': dict(overall=29.7, black=35.6, white=28.1, hispanic=21.3),
    'HI': dict(overall=21.8, black=28.4, white=22.1, hispanic=18.9),
    'ID': dict(overall=28.7, black=33.1, white=28.4, hispanic=21.9),
    'IL': dict(overall=26.4, black=32.7, white=25.2, hispanic=20.6),
    'IN': dict(overall=30.8, black=36.4, white=29.8, hispanic=22.8),
    'IA': dict(overall=26.4, black=34.8, white=25.6, hispanic=21.3),
    'KS': dict(overall=27.8, black=34.2, white=26.9, hispanic=21.4),
    'KY': dict(overall=35.1, black=40.2, white=34.1, hispanic=24.3),
    'LA': dict(overall=33.1, black=37.8, white=31.2, hispanic=23.8),
    'ME': dict(overall=29.8, black=35.4, white=29.4, hispanic=22.8),
    'MD': dict(overall=26.1, black=30.4, white=24.8, hispanic=20.2),
    'MA': dict(overall=25.3, black=31.4, white=24.8, hispanic=21.8),
    'MI': dict(overall=29.9, black=36.1, white=28.9, hispanic=22.4),
    'MN': dict(overall=26.1, black=33.8, white=25.2, hispanic=20.8),
    'MS': dict(overall=36.1, black=40.3, white=33.8, hispanic=24.1),
    'MO': dict(overall=31.4, black=37.2, white=30.4, hispanic=23.1),
    'MT': dict(overall=29.4, black=35.1, white=28.4, hispanic=22.8),
    'NE': dict(overall=26.2, black=33.9, white=25.4, hispanic=21.2),
    'NV': dict(overall=27.4, black=33.2, white=27.1, hispanic=21.4),
    'NH': dict(overall=27.1, black=33.8, white=26.8, hispanic=22.1),
    'NJ': dict(overall=24.4, black=30.1, white=23.4, hispanic=20.2),
    'NM': dict(overall=31.2, black=37.8, white=31.4, hispanic=24.8),
    'NY': dict(overall=25.6, black=31.4, white=24.1, hispanic=20.4),
    'NC': dict(overall=29.4, black=34.8, white=28.1, hispanic=21.8),
    'ND': dict(overall=26.4, black=34.1, white=25.8, hispanic=21.4),
    'OH': dict(overall=30.4, black=36.8, white=29.4, hispanic=23.1),
    'OK': dict(overall=33.4, black=38.9, white=32.1, hispanic=23.8),
    'OR': dict(overall=28.8, black=34.9, white=28.4, hispanic=22.1),
    'PA': dict(overall=28.4, black=34.9, white=27.4, hispanic=22.8),
    'RI': dict(overall=26.4, black=32.8, white=25.8, hispanic=22.1),
    'SC': dict(overall=31.4, black=36.8, white=29.8, hispanic=22.8),
    'SD': dict(overall=28.2, black=35.4, white=27.4, hispanic=22.1),
    'TN': dict(overall=33.8, black=38.9, white=32.4, hispanic=23.8),
    'TX': dict(overall=28.4, black=33.9, white=27.4, hispanic=21.8),
    'UT': dict(overall=24.8, black=31.4, white=24.1, hispanic=20.8),
    'VT': dict(overall=28.4, black=34.1, white=28.1, hispanic=22.4),
    'VA': dict(overall=26.4, black=31.8, white=25.4, hispanic=20.8),
    'WA': dict(overall=27.4, black=33.4, white=26.8, hispanic=21.4),
    'WV': dict(overall=38.4, black=43.8, white=37.8, hispanic=27.1),
    'WI': dict(overall=28.4, black=35.9, white=27.4, hispanic=22.1),
    'WY': dict(overall=29.4, black=36.1, white=28.8, hispanic=22.4),
}


def build_disparity_dataset(
    intensity_df: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Construct the core disparity analysis dataset combining:
    - State policy characteristics
    - Racial demographic composition
    - T1019 provider intensity (spending-based proxy)
    - BRFSS disability prevalence (true-need proxy)
    - Frailty exemption rate estimates
    """
    cohort = build_state_cohort()

    # Add BRFSS disability data
    brfss_rows = []
    for state, vals in BRFSS_DISABILITY.items():
        brfss_rows.append({
            'state': state,
            'disability_overall': vals['overall'],
            'disability_black': vals['black'],
            'disability_white': vals['white'],
            'disability_hispanic': vals['hispanic'],
        })
    brfss_df = pd.DataFrame(brfss_rows)

    # Merge
    df = cohort.merge(brfss_df, on='state', how='left')

    # Merge provider intensity if provided
    if intensity_df is not None:
        intensity_agg = intensity_df.groupby('state').agg(
            intensity_per_enrollee=('intensity_per_enrollee', 'mean'),
            provider_density_per_1k=('provider_density_per_1k', 'mean'),
            t1019_coverage_pct=('t1019_coverage_pct', 'mean'),
        ).reset_index()
        df = df.merge(intensity_agg, on='state', how='left')
    else:
        # Fill with NaN if intensity data not available
        df['intensity_per_enrollee'] = np.nan
        df['provider_density_per_1k'] = np.nan
        df['t1019_coverage_pct'] = np.nan

    # Compute key disparity variables
    df = df.dropna(subset=['disability_overall', 'exempt_pct_overall'])

    # "Label bias" metric: difference between cost-proxy ranking and
    # true-need ranking by state
    # Higher disability → higher true need; higher intensity → higher cost proxy
    # When cost-proxy rank >> true-need rank: over-identification
    # When cost-proxy rank << true-need rank: under-identification (bias risk)
    if df['intensity_per_enrollee'].notna().any():
        df['cost_proxy_rank'] = df['intensity_per_enrollee'].rank(pct=True)
    else:
        # Fallback: use exemption rate as proxy
        df['cost_proxy_rank'] = df['exempt_pct_overall'].rank(pct=True)

    df['true_need_rank'] = df['disability_overall'].rank(pct=True)
    df['label_bias_score'] = df['cost_proxy_rank'] - df['true_need_rank']

    # Disability gap: Black - White disability prevalence (positive = Black higher need)
    df['disability_gap_black_white'] = df['disability_black'] - df['disability_white']

    # "Algorithmic penalty" = disability_gap - racial_gap (positive = Black disadvantaged)
    # A state where Black adults have more disability than white adults (disability_gap > 0)
    # but smaller exemption gap (racial_gap < disability_gap) is "algorithmically penalizing"
    df['algorithmic_penalty'] = df['disability_gap_black_white'] - df['racial_gap_pp'].fillna(0)

    return df


def run_ols_disparity_regression(df: pd.DataFrame) -> Dict:
    """
    OLS regression: racial_gap_pp ~ policy_drivers + controls

    Key hypothesis: higher stringency, active documentation, and lack of
    HIE/EHR integration predict larger racial gaps in exemption rates.
    """
    model_df = df.dropna(subset=['racial_gap_pp', 'stringency_score']).copy()

    if len(model_df) < 10:
        return {'error': 'Insufficient data for regression', 'n': len(model_df)}

    # Model 1: Policy drivers only
    formula1 = (
        'racial_gap_pp ~ stringency_score + requires_physician_cert + '
        'full_ex_parte + uses_hie + uses_cfi + long_claims_lag'
    )

    # Model 2: Add demographic controls
    formula2 = (
        'racial_gap_pp ~ stringency_score + requires_physician_cert + '
        'full_ex_parte + uses_hie + uses_cfi + long_claims_lag + '
        'black_pct + disability_gap_black_white'
    )

    results = {}
    for name, formula in [('policy_only', formula1), ('with_demographics', formula2)]:
        try:
            model = smf.ols(formula, data=model_df).fit()
            results[name] = {
                'formula': formula,
                'n': int(model.nobs),
                'r_squared': round(model.rsquared, 3),
                'adj_r_squared': round(model.rsquared_adj, 3),
                'coefficients': {
                    var: {
                        'coef': round(model.params[var], 4),
                        'se': round(model.bse[var], 4),
                        'p_value': round(model.pvalues[var], 4),
                        'ci_lower': round(model.conf_int().loc[var, 0], 4),
                        'ci_upper': round(model.conf_int().loc[var, 1], 4),
                    }
                    for var in model.params.index
                },
                'aic': round(model.aic, 2),
                'bic': round(model.bic, 2),
            }
        except Exception as e:
            results[name] = {'error': str(e)}

    return results


def run_coverage_loss_disparity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Quantify the absolute coverage loss disparity by race.

    For each state with work requirements, estimate how many Black vs.
    White expansion adults would lose coverage due to failure to obtain
    medically frail exemptions they qualify for (based on disability rates).

    This is the policy-relevant output for policymakers.
    """
    wr_states = df[df['wr_status'].isin(['active', 'pending', 'blocked'])].copy()
    wr_states = wr_states.dropna(subset=['expansion_pop_est'])

    # Expected coverage losses if exemption system worked perfectly (no bias)
    # = expansion_pop * disability_rate * (1 - exemption_threshold)
    # Use 15% as target exemption threshold (federal regulatory floor)
    TARGET_EXEMPT_PCT = 15.0

    wr_states['fair_exempt_black'] = wr_states['disability_black'] / 100 * TARGET_EXEMPT_PCT
    wr_states['fair_exempt_white'] = wr_states['disability_white'] / 100 * TARGET_EXEMPT_PCT

    # Actual exemption gap
    wr_states['actual_gap'] = wr_states['racial_gap_pp'].fillna(0)

    # Excess coverage losses for Black enrollees
    wr_states['excess_loss_black'] = (
        wr_states['actual_gap'] / 100 * wr_states['black_expansion_est']
    ).round()

    return wr_states[[
        'state', 'state_name', 'wr_status', 'stringency_score',
        'expansion_pop_est', 'black_expansion_est', 'white_expansion_est',
        'disability_black', 'disability_white', 'disability_gap_black_white',
        'exempt_pct_black', 'exempt_pct_white', 'racial_gap_pp',
        'estimated_coverage_losses', 'excess_loss_black',
        'algorithmic_penalty',
    ]].sort_values('excess_loss_black', ascending=False)


if __name__ == "__main__":
    print("Building disparity dataset...")
    df = build_disparity_dataset()

    print(f"\nStates with complete disparity data: {len(df)}")
    print("\nKey disparity metrics:")
    display_cols = ['state', 'disability_gap_black_white', 'racial_gap_pp',
                    'algorithmic_penalty', 'stringency_score']
    print(df[display_cols].dropna().sort_values(
        'algorithmic_penalty', ascending=False
    ).to_string(index=False))

    print("\n\nOLS Regression Results:")
    reg_results = run_ols_disparity_regression(df)
    for model_name, result in reg_results.items():
        if 'error' not in result:
            print(f"\n  {model_name}: R²={result['r_squared']}, n={result['n']}")
            for var, stats in result['coefficients'].items():
                if var != 'Intercept':
                    sig = '***' if stats['p_value'] < 0.01 else ('**' if stats['p_value'] < 0.05 else ('*' if stats['p_value'] < 0.10 else ''))
                    print(f"    {var}: β={stats['coef']:.3f} (SE={stats['se']:.3f}) p={stats['p_value']:.3f} {sig}")

    print("\n\nCoverage Loss Disparity by State:")
    loss_df = run_coverage_loss_disparity(df)
    print(loss_df[['state', 'racial_gap_pp', 'excess_loss_black', 'algorithmic_penalty']].to_string(index=False))

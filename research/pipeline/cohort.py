"""
Cohort Construction Module
==========================
Replicates the T-MSIS TAF cohort construction logic described in the
OBBBA medically frail bias analysis framework.

In a full implementation with ResDAC-access TAF data, this module would:
1. Filter the TAF Demographic (DE) files for ages 19-64 in expansion states
2. Link eligibility spans to identify continuous enrollment periods
3. Apply OBBBA eligibility criteria (expansion adults, not pregnant, not Medicare dual)

For this analysis, we construct the cohort using:
- CMS MBES enrollment data (public) for state-level enrollment counts
- KFF demographics for racial/ethnic composition
- State frailty definitions for policy characterization
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.kff_medicaid_demographics import load_kff_demographics
from frailty_definitions.state_definitions import (
    STATE_FRAILTY_DEFINITIONS,
    ExparteDetermination,
    ClaimsLag,
)

# States that have or have proposed OBBBA-relevant work requirements
# (expansion states with active, pending, or proposed programs as of 2025)
WORK_REQUIREMENT_STATES = {
    # (state_code, year_of_program_status, status)
    'GA': (2023, 'active'),
    'AR': (2018, 'terminated'),
    'KY': (2018, 'blocked'),
    'MT': (2019, 'active'),
    'AZ': (2024, 'pending'),
    'IN': (2018, 'active'),
    'OH': (2024, 'pending'),
    'MI': (2018, 'blocked'),
    'OK': (2024, 'pending'),
    'TN': (2023, 'pending'),
    'WI': (2018, 'blocked'),
    'NC': (2023, 'active'),
    'LA': (2024, 'pending'),
    'TX': (2024, 'pending'),
    'FL': (2024, 'pending'),
}

# Non-expansion states (no Medicaid expansion as of 2025) — excluded from
# primary expansion-population analysis but included in supplementary analysis
NON_EXPANSION_STATES = {'TX', 'FL', 'GA', 'AL', 'MS', 'SC', 'TN', 'WY', 'SD', 'WI'}
# Note: GA expanded July 2023 (Pathways, limited expansion); TX/FL did not expand

# Expansion states with large Medicaid populations used as comparators
COMPARATOR_STATES = ['CA', 'NY', 'IL', 'PA', 'OH', 'MI', 'WA', 'MD', 'CO', 'MN']


def build_state_policy_index() -> pd.DataFrame:
    """
    Build a state-level policy characterization index combining:
    - Frailty definition stringency
    - Ex parte determination approach
    - Data integration quality
    - Documentation burden

    This serves as the primary policy independent variable in DiD analyses.
    """
    rows = []
    for defn in STATE_FRAILTY_DEFINITIONS:
        # Binary indicators for regression
        full_ex_parte = int(defn.ex_parte_determination == ExparteDetermination.FULL)
        active_doc = int(defn.ex_parte_determination == ExparteDetermination.ACTIVE)
        short_lag = int(defn.claims_lag == ClaimsLag.SHORT)
        long_lag = int(defn.claims_lag == ClaimsLag.LONG)
        wr_info = WORK_REQUIREMENT_STATES.get(defn.state_code, (None, 'none'))

        rows.append({
            'state': defn.state_code,
            'state_name': defn.state_name,
            'stringency_score': defn.stringency_score,
            'adl_threshold': defn.adl_threshold,
            'requires_physician_cert': int(defn.requires_physician_cert),
            'requires_prior_auth': int(defn.requires_prior_auth_record),
            'full_ex_parte': full_ex_parte,
            'active_documentation': active_doc,
            'short_claims_lag': short_lag,
            'long_claims_lag': long_lag,
            'uses_hie': int(defn.uses_hie),
            'uses_ehr': int(defn.uses_ehr_data),
            'uses_mds': int(defn.uses_mds_data),
            'uses_cfi': int(defn.uses_claims_frailty_index),
            'n_icd10_families': len(defn.recognized_conditions),
            'wr_year': wr_info[0],
            'wr_status': wr_info[1],
            # Estimated exemption outcomes
            'exempt_pct_overall': defn.estimated_exempt_pct,
            'exempt_pct_black': defn.estimated_black_exempt_pct,
            'exempt_pct_white': defn.estimated_white_exempt_pct,
            'exempt_pct_hispanic': defn.estimated_hispanic_exempt_pct,
        })

    df = pd.DataFrame(rows)

    # Compute racial exemption gap (White - Black percentage points)
    df['racial_gap_pp'] = (
        df['exempt_pct_white'].fillna(np.nan) -
        df['exempt_pct_black'].fillna(np.nan)
    )

    return df


def build_state_cohort() -> pd.DataFrame:
    """
    Construct the primary analysis cohort: state-level panel combining
    policy characteristics with demographic composition.
    """
    demographics = load_kff_demographics()
    policy_index = build_state_policy_index()

    # Merge on state code
    cohort = demographics.merge(policy_index, on='state', how='outer')

    # Compute estimated absolute numbers of affected enrollees by race
    # Under OBBBA, the relevant population is adults 19-64 (expansion pop)
    # We approximate this as 55% of total Medicaid enrollees based on
    # CMS MBES age distribution data (adults 19-64 as share of total)
    cohort['expansion_pop_est'] = (cohort['total_enrollees'] * 0.55).round().astype('Int64')
    cohort['black_expansion_est'] = (cohort['expansion_pop_est'] * cohort['black_pct'] / 100).round().astype('Int64')
    cohort['white_expansion_est'] = (cohort['expansion_pop_est'] * cohort['white_pct'] / 100).round().astype('Int64')
    cohort['hispanic_expansion_est'] = (cohort['expansion_pop_est'] * cohort['hispanic_pct'] / 100).round().astype('Int64')

    # Estimated coverage losses under work requirements
    # Based on Sommers et al. (2019) Arkansas evaluation finding 18k losses
    # from 270k expansion population = 6.7% coverage loss rate
    # Adjusted for exemption rate in each state
    BASE_COVERAGE_LOSS_RATE = 0.067
    cohort['coverage_loss_rate_est'] = BASE_COVERAGE_LOSS_RATE * (
        1 - cohort['exempt_pct_overall'].fillna(15) / 100
    )
    cohort['estimated_coverage_losses'] = (
        cohort['expansion_pop_est'] * cohort['coverage_loss_rate_est']
    ).round().astype('Int64')

    return cohort


if __name__ == "__main__":
    cohort = build_state_cohort()
    print("State Policy Cohort:")
    print(cohort[['state', 'state_name', 'stringency_score', 'racial_gap_pp',
                   'exempt_pct_overall', 'expansion_pop_est',
                   'estimated_coverage_losses']].dropna(
        subset=['stringency_score']
    ).sort_values('racial_gap_pp', ascending=False).to_string(index=False))

"""
ACS PUMS Individual-Level Analysis — PRIMARY need-side dataset
==============================================================
Downloads and processes the Census Bureau ACS 1-Year Public Use Microdata
Sample (PUMS) to produce individual-level disability prevalence estimates
among Medicaid-enrolled working-age adults, stratified by race/ethnicity
and state.

This is the PRIMARY analysis that replaces the ecological BRFSS state×race
aggregate lookup in disparity_analysis.py, directly addressing the ecological
fallacy concern raised in peer review.

Source: U.S. Census Bureau, American Community Survey 1-Year PUMS, 2022
Access: Public, no registration required
Download: https://www2.census.gov/programs-surveys/acs/data/pums/2022/1-Year/

Key variables used:
    AGEP    — Age
    ST      — State FIPS code
    RAC1P   — Race (1=White, 2=Black, 3-5=AIAN, 6=Asian, 7=NHPI, 8=Other, 9=Multi)
    HISP    — Hispanic origin (1=Not Hispanic, 2-24=Hispanic)
    HINS3   — Medicaid/means-tested coverage (1=Yes, 2=No)
    DIS     — Disability recode (1=With disability, 2=Without)
    DPHY    — Ambulatory difficulty (1=Yes, 2=No)
    DREM    — Cognitive difficulty (1=Yes, 2=No)
    DDRS    — Self-care difficulty (1=Yes, 2=No)
    DOUT    — Independent living difficulty (1=Yes, 2=No)
    DEAR    — Hearing difficulty (1=Yes, 2=No)
    DEYE    — Vision difficulty (1=Yes, 2=No)
    POVPIP  — Income-to-poverty ratio (integer, e.g. 100 = 100% FPL)
    SCHL    — Educational attainment
    PWGTP   — Person weight (for population-weighted estimates)

Regression model:
    P(any_disability | race, medicaid=True, state, age_group, income_cat, sex)
    → Individual-level logistic regression, standard errors clustered by state

Output:
    1. Individual-level DataFrame (Medicaid adults 19-64)
    2. State × race prevalence table (weighted, with 95% CIs)
    3. Regression results: Black-White disability gap conditional on covariates
"""

import io
import zipfile
import requests
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

import statsmodels.formula.api as smf

DATA_DIR = Path(__file__).parent
CACHE_FILE = DATA_DIR / "acs_pums_medicaid_adults.parquet"

# Census Bureau ACS 2022 1-Year PUMS — national person file (two parts)
# Combined: ~3.3M person records covering all 50 states + DC + PR
ACS_PUMS_URLS = [
    "https://www2.census.gov/programs-surveys/acs/data/pums/2022/1-Year/csv_pus.zip",
]

# State FIPS → abbreviation mapping
FIPS_TO_STATE = {
    1: 'AL', 2: 'AK', 4: 'AZ', 5: 'AR', 6: 'CA', 8: 'CO', 9: 'CT',
    10: 'DE', 11: 'DC', 12: 'FL', 13: 'GA', 15: 'HI', 16: 'ID', 17: 'IL',
    18: 'IN', 19: 'IA', 20: 'KS', 21: 'KY', 22: 'LA', 23: 'ME', 24: 'MD',
    25: 'MA', 26: 'MI', 27: 'MN', 28: 'MS', 29: 'MO', 30: 'MT', 31: 'NE',
    32: 'NV', 33: 'NH', 34: 'NJ', 35: 'NM', 36: 'NY', 37: 'NC', 38: 'ND',
    39: 'OH', 40: 'OK', 41: 'OR', 42: 'PA', 44: 'RI', 45: 'SC', 46: 'SD',
    47: 'TN', 48: 'TX', 49: 'UT', 50: 'VT', 51: 'VA', 53: 'WA', 54: 'WV',
    55: 'WI', 56: 'WY', 72: 'PR',
}

# Columns to load (subset for memory efficiency)
PUMS_COLS = [
    'AGEP', 'ST', 'RAC1P', 'HISP', 'SEX',
    'HINS3',                          # Medicaid/means-tested insurance
    'DIS',                            # Any disability (summary)
    'DPHY', 'DREM', 'DDRS', 'DOUT',  # ADL/IADL-proximate disabilities
    'DEAR', 'DEYE',                   # Sensory disabilities
    'POVPIP', 'SCHL',                 # Socioeconomic controls
    'PWGTP',                          # Person weight
]


def _download_pums_part(url: str, part_label: str) -> pd.DataFrame:
    """Download one PUMS zip file and return the person-file DataFrame."""
    print(f"  Downloading {part_label} from Census Bureau...")
    resp = requests.get(url, stream=True, timeout=300)
    resp.raise_for_status()

    total = int(resp.headers.get('content-length', 0))
    downloaded = 0
    chunks = []
    for chunk in resp.iter_content(chunk_size=1024 * 1024):
        chunks.append(chunk)
        downloaded += len(chunk)
        if total:
            pct = downloaded / total * 100
            print(f"\r    {downloaded/1e6:.0f} MB / {total/1e6:.0f} MB ({pct:.0f}%)", end='')
    print()

    raw = b''.join(chunks)
    zf = zipfile.ZipFile(io.BytesIO(raw))

    # The national zip contains psam_pusa.csv and psam_pusb.csv
    person_files = [n for n in zf.namelist() if n.startswith('psam_p') and n.endswith('.csv')]
    if not person_files:
        # Fall back: any CSV file
        person_files = [n for n in zf.namelist() if n.endswith('.csv')]

    dfs = []
    for fname in person_files:
        print(f"    Reading {fname}...")
        with zf.open(fname) as f:
            df = pd.read_csv(f, usecols=lambda c: c in PUMS_COLS, low_memory=False)
            dfs.append(df)
        print(f"    → {len(dfs[-1]):,} rows")

    return pd.concat(dfs, ignore_index=True)


def load_raw_pums(force_download: bool = False) -> pd.DataFrame:
    """
    Load ACS PUMS data, using cached version if available.

    Returns the full individual-level DataFrame (all ages, all insurance types).
    Downstream filtering is done in load_medicaid_adults().
    """
    if CACHE_FILE.exists() and not force_download:
        print(f"Loading cached ACS PUMS from {CACHE_FILE}...")
        return pd.read_parquet(CACHE_FILE)

    print("Downloading ACS 2022 1-Year PUMS from Census Bureau...")
    print("(National file: ~200MB compressed, ~1GB uncompressed — may take 5-10 minutes)\n")

    parts = []
    for i, url in enumerate(ACS_PUMS_URLS):
        df = _download_pums_part(url, f"Part {i+1}/{len(ACS_PUMS_URLS)}")
        parts.append(df)

    raw = pd.concat(parts, ignore_index=True)
    print(f"\nRaw PUMS loaded: {len(raw):,} person records")

    # Filter and cache only Medicaid-enrolled working-age adults to save space
    medicaid_adults = _filter_medicaid_adults(raw)
    medicaid_adults.to_parquet(CACHE_FILE, index=False)
    print(f"Cached {len(medicaid_adults):,} Medicaid adults to {CACHE_FILE}")

    return medicaid_adults


def _filter_medicaid_adults(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter to Medicaid-enrolled working-age adults (19-64).
    Apply race/ethnicity classification.
    """
    # Working-age adults
    df = df[(df['AGEP'] >= 19) & (df['AGEP'] <= 64)].copy()

    # Medicaid/means-tested coverage (HINS3=1)
    df = df[df['HINS3'] == 1].copy()

    # Exclude Puerto Rico (FIPS 72) — different Medicaid rules
    df = df[df['ST'] != 72].copy()

    # State abbreviation
    df['state'] = df['ST'].map(FIPS_TO_STATE)

    # Race/ethnicity classification (standard OMB categories)
    # Priority: Hispanic ethnicity first, then race
    def classify_race(row):
        if row['HISP'] > 1:
            return 'hispanic'
        r = row['RAC1P']
        if r == 1:
            return 'white'
        elif r == 2:
            return 'black'
        elif r in (3, 4, 5):
            return 'aian'
        elif r == 6:
            return 'asian'
        elif r == 7:
            return 'nhpi'
        else:
            return 'other'

    df['race_eth'] = df.apply(classify_race, axis=1)

    # Binary disability indicators (1=Yes in PUMS, 2=No)
    for col in ['DIS', 'DPHY', 'DREM', 'DDRS', 'DOUT', 'DEAR', 'DEYE']:
        if col in df.columns:
            df[f'{col}_bin'] = (df[col] == 1).astype(int)

    # ADL/IADL proxy: any of ambulatory, self-care, independent living, cognitive
    adl_cols = [c for c in ['DPHY_bin', 'DDRS_bin', 'DOUT_bin', 'DREM_bin'] if c in df.columns]
    if adl_cols:
        df['adl_iadl_disability'] = (df[adl_cols].sum(axis=1) >= 1).astype(int)

    # Age groups for regression
    df['age_group'] = pd.cut(
        df['AGEP'],
        bins=[18, 29, 39, 49, 59, 64],
        labels=['19-29', '30-39', '40-49', '50-59', '60-64']
    ).astype(str)

    # Income category (FPL bands)
    df['income_cat'] = pd.cut(
        df['POVPIP'].fillna(0),
        bins=[-1, 50, 100, 138, 200, 400, 9999],
        labels=['<50%', '50-100%', '100-138%', '138-200%', '200-400%', '>400%']
    ).astype(str)

    # Education (simplified)
    df['college_plus'] = (df['SCHL'].fillna(0) >= 21).astype(int)

    return df


def load_medicaid_adults(force_download: bool = False) -> pd.DataFrame:
    """
    Main entry point. Returns individual-level DataFrame of Medicaid-enrolled
    adults 19-64 with disability indicators and race/ethnicity.
    """
    return load_raw_pums(force_download=force_download)


def compute_state_race_prevalence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute weighted disability prevalence by state × race, with 95% CIs
    using normal approximation on the weighted proportions.

    Returns a DataFrame with columns:
        state, race_eth, n_unweighted, n_weighted,
        disability_pct, adl_iadl_pct,
        disability_ci_lower, disability_ci_upper
    """
    rows = []
    for (state, race), grp in df.groupby(['state', 'race_eth']):
        if len(grp) < 30:  # suppress small cells
            continue

        w = grp['PWGTP'].fillna(1)
        n_uw = len(grp)
        n_w = w.sum()

        # Weighted prevalence
        dis_pct = (grp['DIS_bin'] * w).sum() / n_w * 100
        adl_pct = (grp['adl_iadl_disability'] * w).sum() / n_w * 100 if 'adl_iadl_disability' in grp.columns else np.nan

        # Wilson 95% CI on weighted proportion
        p = dis_pct / 100
        se = np.sqrt(p * (1 - p) / n_uw)
        ci_lo = max(0, (p - 1.96 * se) * 100)
        ci_hi = min(100, (p + 1.96 * se) * 100)

        rows.append({
            'state': state,
            'race_eth': race,
            'n_unweighted': n_uw,
            'n_weighted': int(n_w),
            'disability_pct': round(dis_pct, 2),
            'adl_iadl_pct': round(adl_pct, 2),
            'disability_ci_lower': round(ci_lo, 2),
            'disability_ci_upper': round(ci_hi, 2),
        })

    return pd.DataFrame(rows).sort_values(['state', 'race_eth'])


def compute_black_white_gap(prevalence_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Black–White disability prevalence gap by state.
    Returns state-level table with gap and whether gap is statistically
    significant (non-overlapping CIs as a conservative test).
    """
    black = prevalence_df[prevalence_df['race_eth'] == 'black'].set_index('state')
    white = prevalence_df[prevalence_df['race_eth'] == 'white'].set_index('state')

    common = black.index.intersection(white.index)
    gap = pd.DataFrame({
        'state': common,
        'disability_black_pct': black.loc[common, 'disability_pct'].values,
        'disability_white_pct': white.loc[common, 'disability_pct'].values,
        'adl_iadl_black_pct': black.loc[common, 'adl_iadl_pct'].values,
        'adl_iadl_white_pct': white.loc[common, 'adl_iadl_pct'].values,
        'n_black': black.loc[common, 'n_unweighted'].values,
        'n_white': white.loc[common, 'n_unweighted'].values,
    })

    gap['bw_disability_gap_pp'] = gap['disability_black_pct'] - gap['disability_white_pct']
    gap['bw_adl_gap_pp'] = gap['adl_iadl_black_pct'] - gap['adl_iadl_white_pct']

    return gap.sort_values('bw_disability_gap_pp', ascending=False).reset_index(drop=True)


def run_individual_logistic_regression(df: pd.DataFrame) -> dict:
    """
    Logistic regression: P(disability | race, state_FE, age_group, income_cat)
    Among Medicaid-enrolled adults 19-64.

    Key coefficient of interest: race_eth[T.black] — the Black–White
    disability gap conditional on age, income, and state fixed effects.

    This is the individual-level test the ecological analysis cannot perform.
    Standard errors are HC1 (heteroskedasticity-robust).
    """
    model_df = df[df['race_eth'].isin(['black', 'white'])].copy()
    model_df['black'] = (model_df['race_eth'] == 'black').astype(int)
    model_df = model_df.dropna(subset=['DIS_bin', 'black', 'age_group', 'income_cat', 'state'])

    if len(model_df) < 1000:
        return {'error': 'Insufficient data for individual-level regression', 'n': len(model_df)}

    # Model 1: race + state FE only
    formula1 = 'DIS_bin ~ black + C(state)'

    # Model 2: + age + income controls
    formula2 = 'DIS_bin ~ black + C(state) + C(age_group) + C(income_cat)'

    # Model 3: + education (socioeconomic confounder per Reviewer 3)
    formula3 = 'DIS_bin ~ black + C(state) + C(age_group) + C(income_cat) + college_plus'

    results = {}
    for name, formula in [
        ('unadjusted_state_FE', formula1),
        ('age_income_adjusted', formula2),
        ('fully_adjusted', formula3),
    ]:
        try:
            model = smf.logit(formula, data=model_df).fit(
                cov_type='HC1', disp=False, maxiter=100
            )
            # Marginal effect at mean for 'black'
            me = model.get_margeff()
            black_idx = [i for i, n in enumerate(me.summary_frame().index) if 'black' in str(n)]

            results[name] = {
                'n': int(model.nobs),
                'aic': round(model.aic, 1),
                'black_coef_log_odds': round(model.params.get('black', np.nan), 4),
                'black_or': round(np.exp(model.params.get('black', np.nan)), 3),
                'black_p_value': round(model.pvalues.get('black', np.nan), 4),
                'black_ci_lower_or': round(np.exp(model.conf_int().loc['black', 0]), 3) if 'black' in model.conf_int().index else np.nan,
                'black_ci_upper_or': round(np.exp(model.conf_int().loc['black', 1]), 3) if 'black' in model.conf_int().index else np.nan,
                'black_marginal_effect_pp': round(
                    me.margeff[black_idx[0]] * 100, 2
                ) if black_idx else np.nan,
            }
        except Exception as e:
            results[name] = {'error': str(e), 'n': len(model_df)}

    return results


if __name__ == "__main__":
    print("=" * 60)
    print("ACS PUMS Individual-Level Disability Analysis (Primary)")
    print("Source: Census Bureau ACS 1-Year PUMS 2022")
    print("=" * 60 + "\n")

    df = load_medicaid_adults()
    print(f"\nMedicaid adults 19-64: {len(df):,} individual records")
    print(f"States covered: {df['state'].nunique()}")
    print(f"\nRace/ethnicity distribution:")
    print(df['race_eth'].value_counts().to_string())

    print("\n\nWeighted disability prevalence by state × race (top states):")
    prev = compute_state_race_prevalence(df)
    print(prev[prev['race_eth'].isin(['black', 'white'])].head(20).to_string(index=False))

    print("\n\nBlack-White disability gap (individual-level, Medicaid adults):")
    gap = compute_black_white_gap(prev)
    print(gap[['state', 'disability_black_pct', 'disability_white_pct',
               'bw_disability_gap_pp', 'bw_adl_gap_pp', 'n_black', 'n_white']].head(20).to_string(index=False))

    print("\n\nIndividual-level logistic regression results:")
    reg = run_individual_logistic_regression(df)
    for model_name, res in reg.items():
        if 'error' not in res:
            print(f"\n  {model_name} (n={res['n']:,}):")
            print(f"    Black OR = {res['black_or']} "
                  f"(95% CI: {res['black_ci_lower_or']}–{res['black_ci_upper_or']}, "
                  f"p={res['black_p_value']:.4f})")
            print(f"    Marginal effect: +{res['black_marginal_effect_pp']:.1f} pp higher "
                  f"disability prevalence for Black vs. White Medicaid adults")

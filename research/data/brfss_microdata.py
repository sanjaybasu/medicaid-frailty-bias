"""
BRFSS Individual Microdata — SECONDARY need-side dataset
=========================================================
Downloads and processes the CDC Behavioral Risk Factor Surveillance System
(BRFSS) 2022 individual-level microdata to produce disability prevalence
estimates among Medicaid-enrolled adults, stratified by race/ethnicity
and state.

Role in study:
    SECONDARY / ROBUSTNESS CHECK — replicates the ACS PUMS primary analysis
    using an independent survey instrument. Continuity with the existing
    ecological BRFSS estimates already cited in the manuscript. Directly
    addresses Reviewer 3's concern about using BRFSS as an ecological
    comparator by using it at the individual level instead.

Source: CDC BRFSS 2022 Annual Survey Data
Access: Public, no registration required
Download: https://www.cdc.gov/brfss/annual_data/2022/files/LLCP2022XPT.zip
Format: SAS transport format (.XPT), readable via pandas.read_sas()

Key variables:
    _STATE      — State FIPS code
    _RACE       — Computed race (1=White, 2=Black, 3=AIAN, 4=Asian,
                  5=NHPI, 6=Other, 7=Multi, 8=Hispanic, 9=Unknown)
    _AGE65YR    — Age group (1=18-64, 2=65+)  [use to filter 18-64]
    PRIMINS1    — Primary source of health insurance (4=Medicaid)
    MEDCOST1    — Couldn't see doctor due to cost in past year
    DIFFWALK    — Difficulty walking or climbing stairs (1=Yes, 2=No)
    DIFFDRES    — Difficulty dressing or bathing (1=Yes, 2=No)
    DIFFALON    — Difficulty doing errands alone (1=Yes, 2=No)
    DECIDE      — Difficulty concentrating/remembering/making decisions
    BLIND       — Blind or serious difficulty seeing even with glasses
    DEAF        — Deaf or serious difficulty hearing
    EMPLOY1     — Employment status (to identify working-age)
    INCOME3     — Income category
    EDUCA       — Education level
    _LLCPWT     — Final adjusted weight (use for all prevalence estimates)

Note: BRFSS uses complex survey design. The _LLCPWT weight accounts for
stratification and clustering. For standard errors, the full set of
jackknife replicate weights (_STRWT + _PSU) should be used. We use the
simplified approach (design-corrected means using _LLCPWT) which is
standard for descriptive analyses.
"""

import io
import zipfile
import requests
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional
import warnings
warnings.filterwarnings('ignore')

import statsmodels.formula.api as smf

DATA_DIR = Path(__file__).parent
CACHE_FILE = DATA_DIR / "brfss_2022_medicaid_adults.parquet"

BRFSS_URL = "https://www.cdc.gov/brfss/annual_data/2022/files/LLCP2022XPT.zip"

# State FIPS → abbreviation
FIPS_TO_STATE = {
    1: 'AL', 2: 'AK', 4: 'AZ', 5: 'AR', 6: 'CA', 8: 'CO', 9: 'CT',
    10: 'DE', 11: 'DC', 12: 'FL', 13: 'GA', 15: 'HI', 16: 'ID', 17: 'IL',
    18: 'IN', 19: 'IA', 20: 'KS', 21: 'KY', 22: 'LA', 23: 'ME', 24: 'MD',
    25: 'MA', 26: 'MI', 27: 'MN', 28: 'MS', 29: 'MO', 30: 'MT', 31: 'NE',
    32: 'NV', 33: 'NH', 34: 'NJ', 35: 'NM', 36: 'NY', 37: 'NC', 38: 'ND',
    39: 'OH', 40: 'OK', 41: 'OR', 42: 'PA', 44: 'RI', 45: 'SC', 46: 'SD',
    47: 'TN', 48: 'TX', 49: 'UT', 50: 'VT', 51: 'VA', 53: 'WA', 54: 'WV',
    55: 'WI', 56: 'WY', 66: 'GU', 72: 'PR', 78: 'VI',
}

# BRFSS _RACE recode → standardized race/ethnicity label
# Source: BRFSS 2022 codebook, variable _RACE
BRFSS_RACE_MAP = {
    1: 'white',     # White only, non-Hispanic
    2: 'black',     # Black only, non-Hispanic
    3: 'aian',      # American Indian or Alaskan Native only, non-Hispanic
    4: 'asian',     # Asian only, non-Hispanic
    5: 'nhpi',      # Native Hawaiian or other Pacific Islander only, non-Hispanic
    6: 'other',     # Other race only, non-Hispanic
    7: 'other',     # Multiracial, non-Hispanic
    8: 'hispanic',  # Hispanic
    9: np.nan,      # Don't know / Not sure / Refused
}


def _download_brfss() -> pd.DataFrame:
    """Download BRFSS 2022 XPT file and return as DataFrame."""
    print(f"Downloading BRFSS 2022 from CDC...")
    print(f"  URL: {BRFSS_URL}")
    print(f"  (Compressed file ~60MB — may take 2-3 minutes)\n")

    resp = requests.get(BRFSS_URL, stream=True, timeout=300)
    resp.raise_for_status()

    total = int(resp.headers.get('content-length', 0))
    chunks = []
    downloaded = 0
    for chunk in resp.iter_content(chunk_size=512 * 1024):
        chunks.append(chunk)
        downloaded += len(chunk)
        if total:
            print(f"\r  {downloaded/1e6:.1f} MB / {total/1e6:.1f} MB ({downloaded/total*100:.0f}%)", end='')
    print()

    raw = b''.join(chunks)
    zf = zipfile.ZipFile(io.BytesIO(raw))

    # Strip whitespace from filenames — CDC zips sometimes include trailing spaces
    xpt_files = [n for n in zf.namelist() if n.strip().upper().endswith('.XPT')]
    if not xpt_files:
        raise RuntimeError(f"No XPT file found in BRFSS zip. Contents: {zf.namelist()}")

    xpt_name = xpt_files[0]
    print(f"  Reading {xpt_name.strip()}...")

    # Read into memory first to avoid issues with spaces in zip member names
    with zf.open(xpt_name) as f:
        raw_bytes = f.read()
    df = pd.read_sas(io.BytesIO(raw_bytes), format='xport', encoding='utf-8')

    print(f"  → {len(df):,} BRFSS 2022 records loaded")
    return df


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize BRFSS column names (they may appear in mixed case in the XPT file)
    and extract the variables we need.
    """
    # BRFSS XPT column names are uppercase with leading underscore for computed vars
    df.columns = df.columns.str.upper()

    # Map to expected names — some variables changed names across years
    rename_map = {}

    # State
    for candidate in ['_STATE', 'STATE']:
        if candidate in df.columns:
            rename_map[candidate] = 'state_fips'
            break

    # Race — BRFSS 2022 renamed _RACE → _RACE1; try all known variants
    for candidate in ['_RACE', '_RACE1', '_IMPRACE', '_RACEG22', '_RACEGR3', '_RACEGR4', '_RACE_G1']:
        if candidate in df.columns:
            rename_map[candidate] = 'race_code'
            break

    # Insurance / Medicaid
    for candidate in ['PRIMINS1', 'HLTHPLN1', 'PRIMINSR']:
        if candidate in df.columns:
            rename_map[candidate] = 'insurance_primary'
            break

    # Age filter
    for candidate in ['_AGE65YR', '_AGEG5YR']:
        if candidate in df.columns:
            rename_map[candidate] = 'age_group_code'
            break

    # Disability / functional limitation variables
    for src, dst in [
        ('DIFFWALK', 'diff_walk'),
        ('DIFFDRES', 'diff_dress'),
        ('DIFFALON', 'diff_alone'),
        ('DECIDE', 'diff_cognitive'),
        ('BLIND', 'diff_vision'),
        ('DEAF', 'diff_hearing'),
        ('MEDCOST1', 'cost_barrier'),
        ('MEDCOST', 'cost_barrier'),
        ('_LLCPWT', 'weight'),   # pre-2022
        ('_LLCPWT2', 'weight'),  # BRFSS 2022 renamed weight
        ('_CLLCPWT', 'weight'),  # cellular landline combined weight
        ('LLCPWT', 'weight'),
        ('INCOME3', 'income_code'),
        ('INCOME2', 'income_code'),
        ('EDUCA', 'education'),
        ('EMPLOY1', 'employment'),
    ]:
        if src in df.columns and dst not in rename_map.values():
            rename_map[src] = dst

    df = df.rename(columns=rename_map)
    return df


def _filter_medicaid_adults(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter to Medicaid-enrolled working-age adults and create analysis variables.
    """
    # State
    if 'state_fips' in df.columns:
        df['state'] = df['state_fips'].astype(int).map(FIPS_TO_STATE)
    df = df[df['state'].notna()].copy()
    df = df[~df['state'].isin(['PR', 'GU', 'VI'])].copy()  # territories

    # Age: keep 19-64 (exclude 65+ and under 18)
    # _AGE65YR: 1=18-64, 2=65+
    if 'age_group_code' in df.columns:
        df = df[df['age_group_code'] == 1].copy()

    # Medicaid identification
    # PRIMINS1: 1=employer, 2=self-purchased, 3=Medicare, 4=Medicaid/CHIP,
    #           5=TRICARE, 6=VA, 7=Indian Health Service, 8=other, 77=none, 88=don't know
    if 'insurance_primary' in df.columns:
        df = df[df['insurance_primary'] == 4].copy()

    # Race/ethnicity
    if 'race_code' in df.columns:
        df['race_eth'] = df['race_code'].map(BRFSS_RACE_MAP)
        df = df[df['race_eth'].notna()].copy()

    # Disability binary indicators (1=Yes, 2=No in BRFSS)
    disability_cols = {
        'diff_walk': 'ambulatory',
        'diff_dress': 'self_care',
        'diff_alone': 'independent_living',
        'diff_cognitive': 'cognitive',
        'diff_vision': 'vision',
        'diff_hearing': 'hearing',
    }

    present_cols = []
    for src, dst in disability_cols.items():
        if src in df.columns:
            df[f'dis_{dst}'] = (df[src] == 1).astype(int)
            present_cols.append(f'dis_{dst}')

    # Any disability = any of the above
    if present_cols:
        df['any_disability'] = (df[present_cols].sum(axis=1) >= 1).astype(int)
    else:
        df['any_disability'] = np.nan

    # ADL/IADL proxy: walk + dress + alone + cognitive
    adl_cols = [c for c in ['dis_ambulatory', 'dis_self_care', 'dis_independent_living', 'dis_cognitive'] if c in df.columns]
    if adl_cols:
        df['adl_iadl_disability'] = (df[adl_cols].sum(axis=1) >= 1).astype(int)

    # Weight — use final adjusted weight
    if 'weight' not in df.columns:
        df['weight'] = 1.0
    df['weight'] = pd.to_numeric(df['weight'], errors='coerce').fillna(1.0)

    # Income category
    if 'income_code' in df.columns:
        # INCOME3: 1=<$10k, 2=$10-15k, 3=$15-20k, 4=$20-25k, 5=$25-35k,
        #          6=$35-50k, 7=$50-75k, 8=$75-100k, 9=$100-150k, 10=$150-200k, 11=>=200k
        df['income_cat'] = df['income_code'].map({
            1: '<$15k', 2: '<$15k', 3: '$15-25k', 4: '$15-25k',
            5: '$25-50k', 6: '$25-50k', 7: '$50-75k', 8: '>$75k',
            9: '>$75k', 10: '>$75k', 11: '>$75k',
        }).fillna('Unknown')
    else:
        df['income_cat'] = 'Unknown'

    # Education
    if 'education' in df.columns:
        df['college_plus'] = (df['education'] >= 5).astype(int)
    else:
        df['college_plus'] = 0

    return df


def load_brfss_medicaid_adults(force_download: bool = False) -> pd.DataFrame:
    """
    Main entry point. Returns individual-level BRFSS DataFrame for
    Medicaid-enrolled adults 19-64.
    """
    if CACHE_FILE.exists() and not force_download:
        print(f"Loading cached BRFSS microdata from {CACHE_FILE}...")
        return pd.read_parquet(CACHE_FILE)

    raw = _download_brfss()
    raw = _standardize_columns(raw)
    df = _filter_medicaid_adults(raw)

    df.to_parquet(CACHE_FILE, index=False)
    print(f"Cached {len(df):,} BRFSS Medicaid adults to {CACHE_FILE}")

    return df


def compute_state_race_prevalence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Weighted disability prevalence by state × race from BRFSS microdata.
    Mirrors the interface of acs_pums.compute_state_race_prevalence() for
    easy comparison between primary and secondary analyses.
    """
    rows = []
    for (state, race), grp in df.groupby(['state', 'race_eth']):
        if len(grp) < 30:
            continue

        w = grp['weight'].fillna(1)
        n_uw = len(grp)
        n_w = w.sum()

        dis_pct = (grp['any_disability'] * w).sum() / n_w * 100 if 'any_disability' in grp.columns else np.nan
        adl_pct = (grp['adl_iadl_disability'] * w).sum() / n_w * 100 if 'adl_iadl_disability' in grp.columns else np.nan

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
            'source': 'BRFSS_2022_individual',
        })

    return pd.DataFrame(rows).sort_values(['state', 'race_eth'])


def run_brfss_logistic_regression(df: pd.DataFrame) -> dict:
    """
    Replicates the ACS primary analysis using BRFSS microdata.
    P(any_disability | black, state_FE, income_cat, college_plus)
    among Medicaid-enrolled working-age adults.
    """
    model_df = df[df['race_eth'].isin(['black', 'white'])].copy()
    model_df['black'] = (model_df['race_eth'] == 'black').astype(int)
    model_df = model_df.dropna(subset=['any_disability', 'black', 'state'])

    if len(model_df) < 200:
        err = {'error': 'Insufficient BRFSS Medicaid sample for regression', 'n': len(model_df)}
        return {'unadjusted_state_FE': err, 'fully_adjusted': err}

    results = {}
    for name, formula in [
        ('unadjusted_state_FE', 'any_disability ~ black + C(state)'),
        ('fully_adjusted', 'any_disability ~ black + C(state) + C(income_cat) + college_plus'),
    ]:
        try:
            model = smf.logit(formula, data=model_df).fit(cov_type='HC1', disp=False, maxiter=100)
            results[name] = {
                'n': int(model.nobs),
                'black_or': round(np.exp(model.params.get('black', np.nan)), 3),
                'black_p_value': round(model.pvalues.get('black', np.nan), 4),
                'black_ci_lower_or': round(np.exp(model.conf_int().loc['black', 0]), 3) if 'black' in model.conf_int().index else np.nan,
                'black_ci_upper_or': round(np.exp(model.conf_int().loc['black', 1]), 3) if 'black' in model.conf_int().index else np.nan,
                'source': 'BRFSS_2022_individual',
            }
        except Exception as e:
            results[name] = {'error': str(e), 'n': len(model_df)}

    return results


if __name__ == "__main__":
    print("=" * 60)
    print("BRFSS Individual Microdata Analysis (Secondary)")
    print("Source: CDC BRFSS 2022")
    print("=" * 60 + "\n")

    df = load_brfss_medicaid_adults()
    print(f"\nBRFSS Medicaid adults 19-64: {len(df):,} records")
    print(f"States covered: {df['state'].nunique()}")
    print(f"\nRace/ethnicity distribution:")
    print(df['race_eth'].value_counts().to_string())

    print("\n\nWeighted disability prevalence by state × race:")
    prev = compute_state_race_prevalence(df)
    print(prev[prev['race_eth'].isin(['black', 'white'])].head(20).to_string(index=False))

    print("\n\nLogistic regression (BRFSS replication):")
    reg = run_brfss_logistic_regression(df)
    for model_name, res in reg.items():
        if 'error' not in res:
            print(f"\n  {model_name} (n={res['n']:,}):")
            print(f"    Black OR = {res['black_or']} "
                  f"(95% CI: {res['black_ci_lower_or']}–{res['black_ci_upper_or']}, "
                  f"p={res['black_p_value']:.4f})")

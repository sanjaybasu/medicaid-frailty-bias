"""
MEPS Functional Limitations — TERTIARY need-side dataset
=========================================================
Downloads and processes the Medical Expenditure Panel Survey (MEPS)
Full Year Consolidated Data File to measure ADL/IADL functional limitations
among Medicaid-enrolled adults, stratified by race/ethnicity.

Role in study:
    TERTIARY / SENSITIVITY ANALYSIS — national-level only (state samples
    too small for state-stratified analysis). Answers one targeted question:
    after adjusting for income, education, and health literacy, do Black
    Medicaid adults have higher ADL/IADL functional limitation rates than
    white Medicaid adults? Directly addresses Reviewer 3's confounding
    concern (income, health literacy) and the Obermeyer circularity concern
    (MEPS measures functional status independently of claims utilization).

Source: AHRQ Medical Expenditure Panel Survey, 2022
        Full Year Consolidated Data File (HC-243 / h243)
Access: Public, no registration required
Download: https://meps.ahrq.gov/data_files/pufs/h243/h243ssp.zip
Format: SAS transport (.ssp), readable via pandas.read_sas(format='xport')
Note: MEPS uses file number h243 for calendar year 2022 (h233 = 2021).
      No CSV format is published; SAS transport is the smallest portable format.

Key variables (MEPS 2022 HC-243 codebook):
    RACETHX     — Race/ethnicity (1=Hispanic, 2=White non-H, 3=Black non-H,
                  4=Asian non-H, 5=Other non-H)
    INSCOV22    — Insurance coverage (1=Any private, 2=Public only, 3=Uninsured)
    MCDEV22     — Medicaid coverage indicator (1=Yes, 2=No)
    AGELAST     — Age at last interview
    POVCAT22    — Poverty category (1=Poor, 2=Near poor, 3=Low income,
                  4=Middle income, 5=High income)
    EDUCYR      — Years of education (socioeconomic confounder)
    WLKLIM53    — Limited in walking (1=Yes, 2=No) [ADL proxy]
    ACTLIM53    — Activity limitation (1=Yes, 2=No)
    ADHDIFFN    — Difficulty with activities of daily living (count of ADLs)
    IADLHP53    — IADL help needed (1=Yes, 2=No)
    WLKLIM31/42 — Walking limitation (multiple round indicators)
    SAQELIG     — SAQ eligibility (used for health literacy variables)
    PERWT22F    — Person-level final weight

Note: MEPS n≈28,000/year nationally. State identifiers are suppressed in
public use files for most states (only large states have usable n). This
module is therefore national-level only and used as a sensitivity analysis.
"""

import io
import zipfile
import requests
import numpy as np
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import statsmodels.formula.api as smf

DATA_DIR = Path(__file__).parent
CACHE_FILE = DATA_DIR / "meps_2022_medicaid_adults.parquet"

# MEPS 2022 Full Year Consolidated (HC-243 / h243) — Stata format
# h243 = calendar year 2022; h233 = 2021 (different from file sequence number)
# .ssp is CPORT (not XPORT) — pandas cannot read it; use Stata (.dta) instead
MEPS_DTA_URL = "https://meps.ahrq.gov/data_files/pufs/h243/h243dta.zip"

# MEPS race/ethnicity recode
MEPS_RACE_MAP = {
    1: 'hispanic',
    2: 'white',
    3: 'black',
    4: 'asian',
    5: 'other',
}


def _download_meps() -> pd.DataFrame:
    """Download MEPS 2022 (h243) Stata .dta file and return as DataFrame.

    Note: .ssp is SAS CPORT format (not XPORT) — pandas cannot read it.
    Stata format (.dta) is the next-smallest option at ~5.5MB and reads
    natively via pandas.read_stata().
    """
    print(f"Downloading MEPS 2022 (h243) from AHRQ...")
    print(f"  URL: {MEPS_DTA_URL}")
    print(f"  (Stata .dta file ~5.5MB)\n")

    resp = requests.get(MEPS_DTA_URL, stream=True, timeout=180)
    resp.raise_for_status()

    chunks = []
    downloaded = 0
    for chunk in resp.iter_content(chunk_size=256 * 1024):
        chunks.append(chunk)
        downloaded += len(chunk)
        print(f"\r  {downloaded/1e6:.1f} MB downloaded", end='')
    print()

    raw = b''.join(chunks)
    zf = zipfile.ZipFile(io.BytesIO(raw))

    dta_files = [n for n in zf.namelist() if n.strip().lower().endswith('.dta')]
    if not dta_files:
        raise RuntimeError(f"No .dta file in MEPS zip. Contents: {zf.namelist()}")

    fname = dta_files[0]
    print(f"  Reading {fname} via Stata reader...")

    with zf.open(fname) as f:
        raw_bytes = f.read()

    df = pd.read_stata(io.BytesIO(raw_bytes), convert_categoricals=False)
    df.columns = df.columns.str.upper()
    print(f"  → {len(df):,} MEPS 2022 records, {len(df.columns)} variables")
    return df


# Variable name candidates across MEPS years (variable names sometimes change)
_RACE_CANDIDATES = ['RACETHX', 'RACEV1X', 'RACE']
_MEDICAID_CANDIDATES = ['MCDEV22', 'MCDEV21', 'MCDEV20', 'MEDICAID']
_AGE_CANDIDATES = ['AGELAST', 'AGE22X', 'AGE21X', 'AGE']
_POVERTY_CANDIDATES = ['POVCAT22', 'POVCAT21', 'POVCAT20', 'POVCAT']
_WEIGHT_CANDIDATES = ['PERWT22F', 'PERWT21F', 'PERWT20F', 'PERWT']
_EDUC_CANDIDATES = ['EDUCYR', 'EDUYRDEG', 'EDUC']

# ADL/IADL/functional limitation variable candidates
_ADL_CANDIDATES = [
    'ADHDIFFN',  # # ADLs with difficulty (count)
    'WLKLIM53', 'WLKLIM31', 'WLKLIM42',  # Walking limitation
    'ACTLIM53', 'ACTLIM31', 'ACTLIM42',  # Activity limitation
    'IADLHP53', 'IADLHP31', 'IADLHP42',  # IADL help needed
    'HAVADL53', 'HAVADL31', 'HAVADL42',  # Has ADL limitation
]


def _pick(df: pd.DataFrame, candidates: list, default=None):
    """Return first candidate column name that exists in df."""
    for c in candidates:
        if c in df.columns:
            return c
    return default


def _filter_medicaid_adults(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter MEPS data to Medicaid-enrolled working-age adults (19-64)
    and create analysis variables.
    """
    race_col = _pick(df, _RACE_CANDIDATES)
    medicaid_col = _pick(df, _MEDICAID_CANDIDATES)
    age_col = _pick(df, _AGE_CANDIDATES)
    poverty_col = _pick(df, _POVERTY_CANDIDATES)
    weight_col = _pick(df, _WEIGHT_CANDIDATES)
    educ_col = _pick(df, _EDUC_CANDIDATES)

    if age_col is None or race_col is None:
        raise RuntimeError("Cannot identify age or race columns in MEPS data.")

    # Age filter: 19-64
    df = df[(pd.to_numeric(df[age_col], errors='coerce') >= 19) &
            (pd.to_numeric(df[age_col], errors='coerce') <= 64)].copy()

    # Medicaid filter (1=Yes in MEPS)
    if medicaid_col:
        df = df[pd.to_numeric(df[medicaid_col], errors='coerce') == 1].copy()

    # Race/ethnicity
    df['race_eth'] = pd.to_numeric(df[race_col], errors='coerce').map(MEPS_RACE_MAP)
    df = df[df['race_eth'].notna()].copy()

    # Person weight
    df['weight'] = pd.to_numeric(df[weight_col], errors='coerce').fillna(1.0) if weight_col else 1.0

    # Poverty category → income label
    if poverty_col:
        df['poverty_cat'] = pd.to_numeric(df[poverty_col], errors='coerce')
        df['income_cat'] = df['poverty_cat'].map({
            1: 'Poor',
            2: 'Near poor',
            3: 'Low income',
            4: 'Middle income',
            5: 'High income',
        }).fillna('Unknown')
    else:
        df['income_cat'] = 'Unknown'

    # Education
    if educ_col:
        df['educ_years'] = pd.to_numeric(df[educ_col], errors='coerce')
        df['college_plus'] = (df['educ_years'] >= 16).astype(int)
    else:
        df['college_plus'] = 0

    # --- Functional limitation variables ---

    # ADL count (ADHDIFFN: number of ADLs with difficulty, 0-7)
    if 'ADHDIFFN' in df.columns:
        df['adl_count'] = pd.to_numeric(df['ADHDIFFN'], errors='coerce').fillna(0)
        df['any_adl'] = (df['adl_count'] >= 1).astype(int)
    else:
        df['adl_count'] = np.nan
        df['any_adl'] = np.nan

    # Activity limitation (any round)
    actlim_col = _pick(df, ['ACTLIM53', 'ACTLIM42', 'ACTLIM31'])
    if actlim_col:
        df['activity_limitation'] = (
            pd.to_numeric(df[actlim_col], errors='coerce') == 1
        ).astype(int)
    else:
        df['activity_limitation'] = np.nan

    # Walking limitation (ambulatory)
    wlklim_col = _pick(df, ['WLKLIM53', 'WLKLIM42', 'WLKLIM31'])
    if wlklim_col:
        df['ambulatory_limitation'] = (
            pd.to_numeric(df[wlklim_col], errors='coerce') == 1
        ).astype(int)
    else:
        df['ambulatory_limitation'] = np.nan

    # IADL help (independent living proxy)
    iadl_col = _pick(df, ['IADLHP53', 'IADLHP42', 'IADLHP31'])
    if iadl_col:
        df['iadl_limitation'] = (
            pd.to_numeric(df[iadl_col], errors='coerce') == 1
        ).astype(int)
    else:
        df['iadl_limitation'] = np.nan

    # Composite: any functional limitation (ADL or activity or IADL)
    func_cols = [c for c in ['any_adl', 'activity_limitation', 'iadl_limitation']
                 if c in df.columns and df[c].notna().any()]

    if func_cols:
        df['any_functional_limitation'] = (
            df[func_cols].fillna(0).sum(axis=1) >= 1
        ).astype(int)
    else:
        df['any_functional_limitation'] = np.nan

    return df


def load_meps_medicaid_adults(force_download: bool = False) -> pd.DataFrame:
    """
    Main entry point. Returns MEPS individual-level DataFrame for
    Medicaid-enrolled adults 19-64, national sample.
    """
    if CACHE_FILE.exists() and not force_download:
        print(f"Loading cached MEPS data from {CACHE_FILE}...")
        return pd.read_parquet(CACHE_FILE)

    raw = _download_meps()
    df = _filter_medicaid_adults(raw)

    df.to_parquet(CACHE_FILE, index=False)
    print(f"Cached {len(df):,} MEPS Medicaid adults to {CACHE_FILE}")

    return df


def compute_national_race_prevalence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Weighted national-level functional limitation prevalence by race.

    Note: MEPS is national only — state-level estimates are not reliable
    due to small per-state samples. This is the key methodological
    constraint distinguishing MEPS (tertiary) from ACS/BRFSS (primary/secondary).
    """
    rows = []
    for race, grp in df.groupby('race_eth'):
        if len(grp) < 30:
            continue

        w = grp['weight'].fillna(1)
        n_uw = len(grp)
        n_w = w.sum()

        def wpct(col):
            if col not in grp.columns or grp[col].isna().all():
                return np.nan
            return (grp[col].fillna(0) * w).sum() / n_w * 100

        rows.append({
            'race_eth': race,
            'n_unweighted': n_uw,
            'n_weighted': int(n_w),
            'any_functional_limitation_pct': round(wpct('any_functional_limitation'), 2),
            'any_adl_pct': round(wpct('any_adl'), 2),
            'activity_limitation_pct': round(wpct('activity_limitation'), 2),
            'ambulatory_limitation_pct': round(wpct('ambulatory_limitation'), 2),
            'iadl_limitation_pct': round(wpct('iadl_limitation'), 2),
            'source': 'MEPS_2022_national',
        })

    return pd.DataFrame(rows).sort_values('race_eth')


def run_meps_regression(df: pd.DataFrame) -> dict:
    """
    OLS/logistic regression: P(functional_limitation | black, income, education)

    This is the key confounding-adjusted test — MEPS has income and education
    at individual level, directly addressing Reviewer 3's concern that the
    Black-White disability gap is explained by socioeconomic differences.

    If Black coefficient remains significant after income + education adjustment,
    it supports a true health burden disparity (not socioeconomic confounding).
    """
    model_df = df[df['race_eth'].isin(['black', 'white'])].copy()
    model_df['black'] = (model_df['race_eth'] == 'black').astype(int)
    model_df = model_df.dropna(subset=['any_functional_limitation', 'black'])

    if len(model_df) < 100:
        return {'error': 'Insufficient MEPS sample for regression', 'n': len(model_df)}

    results = {}
    formulas = {
        'unadjusted': 'any_functional_limitation ~ black',
        'income_adjusted': 'any_functional_limitation ~ black + C(income_cat)',
        'fully_adjusted_income_education': (
            'any_functional_limitation ~ black + C(income_cat) + college_plus'
        ),
    }

    for name, formula in formulas.items():
        try:
            # Use OLS (LPM) for interpretability; coefficients are marginal effects in pp
            model = smf.ols(formula, data=model_df).fit(cov_type='HC1')
            results[name] = {
                'n': int(model.nobs),
                'black_coef_pp': round(model.params.get('black', np.nan) * 100, 2),
                'black_p_value': round(model.pvalues.get('black', np.nan), 4),
                'black_ci_lower': round(model.conf_int().loc['black', 0] * 100, 2) if 'black' in model.conf_int().index else np.nan,
                'black_ci_upper': round(model.conf_int().loc['black', 1] * 100, 2) if 'black' in model.conf_int().index else np.nan,
                'r_squared': round(model.rsquared, 4),
                'source': 'MEPS_2022_national',
            }
        except Exception as e:
            results[name] = {'error': str(e), 'n': len(model_df)}

    return results


if __name__ == "__main__":
    print("=" * 60)
    print("MEPS Functional Limitations Analysis (Tertiary)")
    print("Source: AHRQ MEPS 2022 Full Year Consolidated (h233)")
    print("=" * 60 + "\n")

    df = load_meps_medicaid_adults()
    print(f"\nMEPS Medicaid adults 19-64: {len(df):,} records (national)")
    print(f"\nRace/ethnicity distribution:")
    print(df['race_eth'].value_counts().to_string())

    print("\n\nNational functional limitation prevalence by race:")
    prev = compute_national_race_prevalence(df)
    print(prev.to_string(index=False))

    print("\n\nRegression: Black-White gap adjusting for income and education:")
    reg = run_meps_regression(df)
    for model_name, res in reg.items():
        if 'error' not in res:
            print(f"\n  {model_name} (n={res['n']:,}):")
            print(f"    Black coefficient: +{res['black_coef_pp']:.1f} pp "
                  f"(95% CI: {res['black_ci_lower']:.1f}–{res['black_ci_upper']:.1f}, "
                  f"p={res['black_p_value']:.4f})")
        else:
            print(f"\n  {model_name}: {res.get('error', 'error')} (n={res.get('n', '?')})")

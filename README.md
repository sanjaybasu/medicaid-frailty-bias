# Racial Disparities in Medicaid Medically Frail Exemption Rates

---

## Requirements

```bash
pip install -r requirements.txt
```

Python 3.10+. No proprietary data are required; all primary data sources are
public. The largest download (ACS PUMS) is approximately 200 MB compressed.

---

## Data Sources

| Dataset | Source | Script |
|---|---|---|
| HHS Medicaid Provider Spending (227M rows, 2018–2024) | opendata.hhs.gov | `data/stream_t1019.py` |
| ACS PUMS 1-Year 2022 (individual disability) | census.gov | `data/acs_pums.py` |
| CDC BRFSS microdata 2022 | cdc.gov/brfss | `data/brfss_microdata.py` |
| MEPS 2022 functional limitations | meps.ahrq.gov | `data/meps_functional.py` |
| KFF Medicaid enrollees by race/ethnicity | kff.org | `data/kff_medicaid_demographics.py` |
| State frailty policy database (17 states) | CMS waiver documents, compiled | `frailty_definitions/state_definitions.py` |
| NPPES NPI→state lookup (billing providers) | npiregistry.cms.hhs.gov | committed as `data/billing_providers.parquet` |

See `data/real_data_sources.md` for URLs, schemas, access notes, and data
quality caveats. Large cached files (ACS, BRFSS, MEPS parquets) are excluded
from the repository by `.gitignore`; download scripts are provided.

---

## Reproducing All Results

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Download T1019 spending data (~2-4 hrs; set HF_TOKEN for higher limits)
python data/stream_t1019.py

# 3. (Optional) Download and cache individual-level disability data
python data/acs_pums.py        # ACS PUMS (~5-10 min)
python data/brfss_microdata.py # BRFSS  (~10-20 min)
python data/meps_functional.py # MEPS   (~5 min)

# 4. Run full analysis pipeline (uses cached parquets if present)
python output/generate_report.py
```

Step 4 uses cached parquets from steps 2–3 if present, or falls back to
pre-specified state-level estimates. All random seeds are fixed at 42;
results are exactly reproducible given identical input data.

Outputs are written to `output/`:
- `pipeline_results.json` — all numeric results (cached)
- `figures/`              — Figures 1–5 (PNG, 200 dpi)
- `tables/`               — Tables 1–5 (CSV)

---

## Running Individual Modules

Each analysis module is also executable independently:

```bash
python pipeline/disparity_analysis.py      # OLS regression, coverage loss
python bias_analysis/fairness_metrics.py   # Calibration, equalized odds, Obermeyer audit
python bias_analysis/algorithm_audit.py    # Monte Carlo algorithm simulation on ACS individuals
python causal_inference/callaway_santanna_did.py  # Staggered DiD
python causal_inference/synthetic_control.py      # Synthetic control (AR, GA, MT)
```

---

## Repository Structure

```
.
├── manuscript.md                        # Full manuscript with tables and references
├── output/appendix.md                   # Supplementary methods and tables
├── requirements.txt
├── data/
│   ├── stream_t1019.py                  # HHS dataset streaming (T1019 by state×month)
│   ├── acs_pums.py                      # ACS PUMS download, filter, disability regression
│   ├── brfss_microdata.py               # BRFSS microdata download and processing
│   ├── meps_functional.py               # MEPS functional limitation module
│   ├── kff_medicaid_demographics.py     # KFF enrollment shares by race/ethnicity
│   ├── billing_providers.parquet        # NPPES NPI→state lookup (committed, 37 MB)
│   └── real_data_sources.md             # Source documentation and data quality notes
├── frailty_definitions/
│   └── state_definitions.py             # 17-state frailty policy database (FrailtyDefinition dataclass)
├── pipeline/
│   ├── cohort.py                        # Expansion cohort construction
│   ├── disparity_analysis.py            # OLS regression and coverage loss estimation
│   └── provider_intensity.py            # T1019 provider density analysis
├── bias_analysis/
│   ├── fairness_metrics.py              # Equalized odds, calibration, Obermeyer audit
│   └── algorithm_audit.py              # Monte Carlo simulation of state algorithms on ACS individuals
├── causal_inference/
│   ├── callaway_santanna_did.py         # Staggered DiD (Callaway & Sant'Anna 2021)
│   └── synthetic_control.py             # Synthetic control (Abadie et al. 2010)
└── output/
    ├── generate_report.py               # Pipeline orchestrator
    ├── pipeline_results.json            # Cached numeric results
    ├── appendix.md                      # Supplementary methods
    ├── figures/                         # PNG figures
    └── tables/                          # CSV tables
```

---

## Notes for Reviewers

- `data/billing_providers.parquet` (37 MB) is committed for convenience; it
  can be regenerated from the NPPES public file at npiregistry.cms.hhs.gov.
- State-level exemption rates are derived from published waiver evaluation
  reports for four states with observed data (GA, AR, IN, NC) and from
  pre-specified researcher estimates for the remaining 12 states. See
  `output/appendix.md` Section A.4 for construction details.
- ResDAC-restricted T-MSIS TAF files would enable individual-level replication
  of the calibration test; the current analysis operates at the state level.
- The T1019 streaming job (`data/stream_t1019.py`) processes 227 million rows
  and takes approximately 2–4 hours without an HF token; set `HF_TOKEN` in
  your environment to increase API rate limits.
- All stochastic operations use fixed seed 42; figures and JSON results are
  exactly reproducible given identical input data.
```

# Racial Disparities in Medicaid Medically Frail Exemption Rates

Multi-state cross-sectional and quasi-experimental analysis of racial disparities in medically frail exemption rates across 17 US states with Medicaid community engagement requirement programs (47.2 million expansion adults, 2016-2024). Applies algorithmic fairness metrics and staggered difference-in-differences to quantify under-identification of Black enrollees as medically frail.

Basu S, Berkowitz SA. 2026.

---

## Requirements

```bash
pip install -r requirements.txt
```

Python 3.10+. No proprietary data are required; all primary data sources are public.

---

## Data Sources

| Dataset | Source | Script |
|---|---|---|
| HHS Medicaid Provider Spending (227M rows, 2018-2024) | opendata.hhs.gov | `data/stream_t1019.py` |
| ACS PUMS 1-Year 2022 (individual disability) | census.gov | `data/acs_pums.py` |
| CDC BRFSS microdata 2022 | cdc.gov/brfss | `data/brfss_microdata.py` |
| MEPS 2022 functional limitations | meps.ahrq.gov | `data/meps_functional.py` |
| KFF Medicaid enrollees by race/ethnicity | kff.org | `data/kff_medicaid_demographics.py` |
| State frailty policy database (17 states) | CMS waiver documents | `frailty_definitions/state_definitions.py` |
| NPPES NPI-to-state lookup | npiregistry.cms.hhs.gov | committed as `data/billing_providers.parquet` |

See `data/real_data_sources.md` for URLs, schemas, and data quality notes.

---

## Reproducing All Results

```bash
pip install -r requirements.txt

# Download T1019 spending data (~2-4 hrs; set HF_TOKEN for higher rate limits)
python data/stream_t1019.py

# Download individual-level disability data (optional; falls back to state-level)
python data/acs_pums.py
python data/brfss_microdata.py
python data/meps_functional.py

# Run full analysis pipeline
python output/generate_report.py
```

All random seeds fixed at 42. Results are exactly reproducible given identical input data.

---

## Running Individual Modules

```bash
python pipeline/disparity_analysis.py
python bias_analysis/fairness_metrics.py
python bias_analysis/algorithm_audit.py
python causal_inference/callaway_santanna_did.py
python causal_inference/synthetic_control.py
```

---

## Repository Structure

```
.
├── requirements.txt
├── data/
│   ├── stream_t1019.py                  # HHS dataset streaming
│   ├── acs_pums.py                      # ACS PUMS download and processing
│   ├── brfss_microdata.py               # BRFSS microdata processing
│   ├── meps_functional.py               # MEPS functional limitations
│   ├── kff_medicaid_demographics.py     # KFF enrollment by race/ethnicity
│   ├── billing_providers.parquet        # NPPES NPI-to-state (committed, 37 MB)
│   └── real_data_sources.md             # Source documentation
├── frailty_definitions/
│   └── state_definitions.py             # 17-state policy database
├── pipeline/
│   ├── cohort.py                        # Expansion cohort construction
│   ├── disparity_analysis.py            # OLS regression, coverage loss estimation
│   └── provider_intensity.py            # T1019 provider density analysis
├── bias_analysis/
│   ├── fairness_metrics.py              # Equalized odds, calibration, Obermeyer audit
│   └── algorithm_audit.py              # Monte Carlo simulation on ACS individuals
├── causal_inference/
│   ├── callaway_santanna_did.py         # Staggered DiD (Callaway and Sant'Anna 2021)
│   └── synthetic_control.py             # Synthetic control (Abadie et al. 2010)
└── output/
    ├── generate_report.py               # Pipeline orchestrator
    ├── pipeline_results.json            # Cached numeric results
    ├── geographic_results.json          # Geographic analysis results
    ├── figures/                         # PNG/PDF figures
    └── tables/                          # CSV tables
```

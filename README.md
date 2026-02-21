# Racial Bias in Medicaid Medically Frail Exemptions

Replication code and data pipeline for:

> Basu S. Algorithmic inequality and racial disparities in medically frail exemptions
> under Medicaid work requirements. *Submitted*, 2026.

---

## Requirements

```
pip install -r research/requirements.txt
```

Python 3.10+. No proprietary data required; all primary data are public.

---

## Data Sources

All data are downloaded automatically on first run or can be retrieved manually:

| Dataset | Source | Access |
|---|---|---|
| HHS Medicaid Provider Spending (227M rows, 2018–2024) | opendata.hhs.gov | Public |
| KFF Medicaid Enrollees by Race/Ethnicity (T-MSIS 2023) | kff.org | Public |
| CDC BRFSS Disability Prevalence (DHDS 2022) | cdc.gov/ncbddd/disabilityandhealth | Public |
| State frailty policy database (17 states) | CMS waiver docs, compiled in-repo | In-repo |
| NPPES billing provider NPI→state lookup | npiregistry.cms.hhs.gov | Public |

See `research/data/real_data_sources.md` for URLs, schema, and data quality notes.

---

## Reproducing the Analysis

```bash
# 1. Download T1019 spending data (streams 227M rows; takes ~2-4 hrs)
python research/data/stream_t1019.py

# 2. Run full pipeline and regenerate all tables, figures, and manuscript
python research/output/generate_report.py
```

Outputs appear in `research/output/`:
- `health_affairs_report.md` — manuscript
- `pipeline_results.json` — all numeric results
- `figures/` — Figures 1–5
- `tables/` — Tables 1–5 as CSV

Individual pipeline modules can be run independently:
```bash
python research/pipeline/disparity_analysis.py
python research/bias_analysis/fairness_metrics.py
python research/causal_inference/callaway_santanna_did.py
python research/causal_inference/synthetic_control.py
```

---

## Repository Structure

```
research/
├── data/
│   ├── stream_t1019.py              # Streams HHS dataset, aggregates T1019 by state×month
│   ├── kff_medicaid_demographics.py # Fetches KFF race/ethnicity enrollment shares
│   ├── billing_providers.parquet    # NPI→state lookup (617K rows, downloaded on first run)
│   └── real_data_sources.md        # Data source documentation
├── frailty_definitions/
│   └── state_definitions.py        # 17-state policy database with FrailtyDefinition dataclass
├── pipeline/
│   ├── cohort.py                   # Expansion cohort construction (TAF-equivalent)
│   ├── disparity_analysis.py       # OLS regression, Oaxaca decomposition, coverage loss
│   └── provider_intensity.py       # T1019 per-enrollee spending and provider density
├── bias_analysis/
│   └── fairness_metrics.py         # Calibration, equalized odds, predictive parity, Obermeyer audit
├── causal_inference/
│   ├── callaway_santanna_did.py    # Staggered DiD (Callaway & Sant'Anna 2021)
│   └── synthetic_control.py        # Synthetic control (Abadie et al. 2010)
└── output/
    ├── generate_report.py           # Main pipeline orchestrator
    ├── health_affairs_report.md     # Manuscript
    ├── pipeline_results.json        # All numeric results (cached)
    ├── figures/                     # PNG figures
    └── tables/                      # CSV tables
```

---

## Notes for Reviewers

- The `billing_providers.parquet` file (37 MB) is committed for convenience; it can be regenerated from NPPES at npiregistry.cms.hhs.gov.
- State-level exemption rates are derived from published waiver evaluation reports, not individual T-MSIS records. Access to ResDAC-restricted TAF files would enable individual-level replication.
- The full T1019 streaming job (`stream_t1019.py`) takes 2–4 hours without an HF token; set `HF_TOKEN` to increase rate limits.
- All random seeds are fixed; results are exactly reproducible given the same data.

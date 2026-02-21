# Medicaid Frailty Bias Research Pipeline

**Target Publication:** Health Affairs
**Title:** Algorithmic Integrity and the Medically Frail Exemption: Evaluating Racial Bias in Post-OBBBA Medicaid Work Requirement Exemption Systems

## Overview

This research package implements a rigorous, FAVES-aligned analytical framework to evaluate racial disparities in medically frail exemption determinations under the One Big Beautiful Bill Act (OBBBA, H.R. 1). It uses **real publicly available data** from:

- **HHS Medicaid Provider Spending Dataset** (227 million billing records, released Feb. 2026) — `opendata.hhs.gov`
- **KFF Medicaid Enrollees by Race/Ethnicity** (2023 T-MSIS Preliminary) — `kff.org`
- **CDC BRFSS Disability Prevalence** (2022 DHDS) — `cdc.gov`
- **State Medicaid Waiver Documents** (SPA filings, 1115 waiver STCs) — `medicaid.gov`

## Key Findings

| Metric | Value |
|--------|-------|
| Mean racial exemption gap (White − Black) | **4.8pp** (SE=0.26) |
| Obermeyer need gap at equal algorithm score | **6.6pp** (p<0.001) |
| DiD effect of work requirement adoption | **+1.2pp** (95% CI: 0.8–1.7) |
| States violating equalized odds | **100%** |
| Estimated excess Black coverage losses | **~224,000** |

## Structure

```
research/
├── frailty_definitions/
│   └── state_definitions.py      # State-level frailty policy database (17 states)
│                                  # From: CMS SPA approvals, 1115 waiver STCs
├── data/
│   ├── kff_medicaid_demographics.py  # KFF race/ethnicity enrollment data (51 states)
│   ├── stream_t1019.py               # Stream T1019 from HHS dataset (~8 min)
│   └── billing_providers.parquet     # NPI→state lookup (auto-downloaded, 617K rows)
├── pipeline/
│   ├── cohort.py                  # TAF-equivalent cohort construction
│   ├── provider_intensity.py      # T1019 spending intensity by state
│   └── disparity_analysis.py      # Disparity regression + coverage loss analysis
├── bias_analysis/
│   └── fairness_metrics.py        # Obermeyer audit, calibration, equalized odds
├── causal_inference/
│   ├── callaway_santanna_did.py   # C&S (2021) staggered DiD
│   └── synthetic_control.py       # Abadie et al. (2010) SCM
└── output/
    ├── generate_report.py         # Main pipeline orchestrator
    ├── health_affairs_report.md   # Generated manuscript
    ├── figures/                   # All manuscript figures (PNG)
    └── tables/                    # All tables (CSV)
```

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Download T1019 spending data (~8 min, streams 227M rows from HHS dataset)
python3 research/data/stream_t1019.py

# Run full analysis pipeline
python3 research/output/generate_report.py
```

## Running Individual Components

```python
# Frailty definitions
from research.frailty_definitions.state_definitions import STATE_FRAILTY_DEFINITIONS

# Disparity analysis
from research.pipeline.disparity_analysis import build_disparity_dataset
df = build_disparity_dataset()

# Fairness metrics
from research.bias_analysis.fairness_metrics import run_full_fairness_evaluation
results = run_full_fairness_evaluation(df)

# Causal inference
from research.causal_inference.callaway_santanna_did import run_staggered_did
did = run_staggered_did()

from research.causal_inference.synthetic_control import run_all_case_studies
scm = run_all_case_studies()
```

## Data Sources

### HHS Medicaid Provider Spending Dataset (Real Data, Public)
- **Release:** February 14, 2026
- **Coverage:** January 2018 – December 2024
- **Size:** 227 million rows, NPI × HCPCS × Month
- **Portal:** https://opendata.hhs.gov/datasets/medicaid-provider-spending/
- **HF Mirror:** https://huggingface.co/datasets/cfahlgren1/medicaid-provider-spending
- **Key code used:** T1019 (Personal Care Services) — $122.7B total spend, 2018-2024

### KFF State Health Facts
- **Indicator:** Medicaid Enrollees by Race/Ethnicity
- **Source data:** T-MSIS RIF, 2023 Preliminary
- **Coverage:** 51 states + DC
- **URL:** https://www.kff.org/medicaid/state-indicator/medicaid-enrollees-by-race-ethnicity/

### CDC BRFSS Disability Prevalence
- **System:** Disability and Health Data System (DHDS)
- **Year:** 2022
- **Measure:** Any disability prevalence, by state and race/ethnicity
- **URL:** https://www.cdc.gov/ncbddd/disabilityandhealth/dhds/

### State Frailty Definition Policy Database
- **Coverage:** 17 states with active, pending, or blocked work requirements
- **Sources:** CMS SPA filings, 1115 waiver STCs, state Medicaid manuals
- **Key references:** Sommers et al. NEJM 2019 (Arkansas); MACPAC 2024; KFF 2024

## Methods

### Analytical Pipeline

1. **Cohort Construction** — Replicates T-MSIS TAF DE file logic for expansion adults 19-64
2. **Provider Intensity** — T1019 spending per enrollee (cost-proxy for frailty algorithm)
3. **Disparity Regression** — OLS regression of racial gap on policy drivers
4. **Obermeyer Audit** — Disability burden vs. algorithm score by race (replicates Science 2019)
5. **Equalized Odds** — TPR/FPR parity across racial groups
6. **Staggered DiD** — Callaway & Sant'Anna (2021) ATT(g,t) estimation
7. **Synthetic Control** — Abadie et al. (2010), Arkansas/Georgia/Montana case studies

### Key References

- Obermeyer Z et al. *Science* 2019;366:447-453. (Racial bias in risk algorithms)
- Callaway B, Sant'Anna PHC. *J Econometrics* 2021;225:200-230. (Staggered DiD)
- Abadie A et al. *JASA* 2010;105:493-505. (Synthetic control)
- Sommers BD et al. *NEJM* 2019;381:1073-1082. (Arkansas waiver evaluation)
- Hardt M et al. *NeurIPS* 2016. (Equalized odds)

## Limitations

1. State-level exemption rate estimates are from waiver evaluations and policy reports, not individual-level T-MSIS data (which requires ResDAC DUA)
2. BRFSS disability is self-reported and may not perfectly match ADL-based frailty criteria
3. Small donor pool limits SCM permutation test power
4. T1019 intensity only available at state level without individual-level linkage

## Note on Data Access

For full replication with individual-level data:
- **T-MSIS TAF files:** Apply at https://resdac.org/
- **MDS (Minimum Data Set):** Apply via CMS Research Data Assistance Center
- **State MMIS data:** Requires state-specific data sharing agreements

## License

MIT License. Research code released for scientific reproducibility.

## Citation

```
[Authors]. Algorithmic Integrity and the Medically Frail Exemption:
Evaluating Racial Bias in Post-OBBBA Medicaid Work Requirement Exemption Systems.
Health Affairs [year].
```

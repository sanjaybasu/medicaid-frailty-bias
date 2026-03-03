# Redesigning Medicaid Frailty Algorithms

Multi-state microsimulation analysis comparing existing and evidence-based redesigned frailty identification algorithms across 17 US states with Medicaid community engagement requirement programs. Uses ACS PUMS individual-level disability data (75,043 Medicaid adults) and a three-channel Monte Carlo microsimulation to estimate algorithm sensitivity and racial equity.

Basu S, Berkowitz SA. Redesigning Medicaid frailty algorithms: improved identification of medically frail adults under community engagement requirements. 2026.

**Key finding:** Existing algorithms identify only 31.4% of functionally disabled adults as medically frail. An evidence-based redesign increases identification to 45.6% (+14.3 pp), narrows the AIAN-White sensitivity gap by 46%, and the Black-White gap by 10%.

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
| ACS PUMS 1-Year 2022 (individual disability) | census.gov | `data/acs_pums.py` |
| HHS Medicaid Provider Spending — T1019 (227M rows) | opendata.hhs.gov | `data/stream_t1019.py` |
| HHS Medicaid Provider Spending — G2211 (227M rows) | opendata.hhs.gov | `data/stream_g2211.py` |
| CDC BRFSS DHDS 2022 (state-race disability) | cdc.gov/brfss | `data/brfss_microdata.py` |
| State frailty policy database (17 states) | CMS waiver documents | `frailty_definitions/state_definitions.py` |
| KFF Medicaid enrollment by race/ethnicity | kff.org | `data/kff_medicaid_demographics.py` |

---

## Reproducing All Results

```bash
pip install -r requirements.txt

# Download ACS PUMS individual-level data
python data/acs_pums.py

# Download T1019 spending data (~2-4 hrs; set HF_TOKEN for higher rate limits)
python data/stream_t1019.py

# Download G2211 visit complexity data (~2-4 hrs)
python data/stream_g2211.py

# Run full reconceptualized analysis pipeline
python run_reconceptualized_pipeline.py
```

All random seeds fixed at 42. Results are exactly reproducible.

---

## Running Individual Modules

```bash
# Core analysis (improved vs status quo)
python bias_analysis/improved_algorithm.py

# G2211 visit complexity validation (eAppendix D)
python bias_analysis/g2211_validation.py

# Legacy analyses (eAppendix)
python bias_analysis/algorithm_audit.py
python bias_analysis/fairness_metrics.py
python pipeline/disparity_analysis.py
python causal_inference/callaway_santanna_did.py
python causal_inference/synthetic_control.py
```

---

## Repository Structure

```
.
├── requirements.txt
├── run_reconceptualized_pipeline.py   # Master pipeline runner
├── data/
│   ├── acs_pums.py                    # ACS PUMS download and processing (75K individuals)
│   ├── stream_t1019.py                # HHS dataset streaming (T1019)
│   ├── stream_g2211.py                # HHS dataset streaming (G2211)
│   ├── brfss_microdata.py             # BRFSS microdata processing
│   ├── meps_functional.py             # MEPS functional limitations
│   ├── kff_medicaid_demographics.py   # KFF enrollment by race/ethnicity
│   └── real_data_sources.md           # Source documentation
├── frailty_definitions/
│   └── state_definitions.py           # 17-state policy database
├── bias_analysis/
│   ├── improved_algorithm.py          # *** Core contribution: redesigned algorithm ***
│   ├── g2211_validation.py            # G2211 visit complexity validation
│   ├── algorithm_audit.py             # Three-channel Monte Carlo engine
│   └── fairness_metrics.py            # Equalized odds, calibration, Obermeyer audit
├── pipeline/
│   ├── cohort.py                      # Expansion cohort construction
│   ├── disparity_analysis.py          # OLS regression, coverage loss estimation
│   └── provider_intensity.py          # T1019 provider density analysis
├── causal_inference/
│   ├── callaway_santanna_did.py       # Staggered DiD (eAppendix)
│   └── synthetic_control.py           # Synthetic control (eAppendix)
├── manuscript/
│   ├── manuscript.md                 # Main text (~2,900 words)
│   ├── appendix.md                   # eAppendix A–D
│   └── cover_letter.md               # Submission cover letter
├── figures/
│   ├── exhibit2_sensitivity_dotplot.* # Main Exhibit 2
│   ├── exhibit3_equity_cobenefit.*    # Main Exhibit 3
│   └── eFigure1–7_*.*                # Appendix eFigures 1–7
└── output/
    ├── improved_algorithm_results.json # Primary results
    ├── g2211_validation_results.json  # G2211 validation results
    ├── pipeline_results.json          # Legacy results
    └── tables/                        # CSV exhibit tables
```

## Key Results

| Metric | Status Quo | Redesigned | Change |
|---|---|---|---|
| Mean sensitivity (17 states) | 31.4% | 45.6% | +14.3 pp |
| White sensitivity | 39.1% | 53.4% | +14.3 pp |
| Black sensitivity | 26.2% | 41.9% | +15.6 pp |
| Hispanic sensitivity | 28.9% | 43.0% | +14.1 pp |
| AIAN sensitivity | 27.5% | 47.1% | +19.6 pp |
| AIAN-White gap | 11.6 pp | 6.3 pp | −5.3 pp (46%) |
| Black-White gap | 12.8 pp | 11.5 pp | −1.3 pp (10%) |
| Additional frail identified | — | — | 3,773,401 |
| Coverage losses averted | — | — | 252,817 |

## Redesigned Algorithm Specification

The redesigned algorithm applies four evidence-based modifications:

1. **Expanded ICD-10**: 13 families (CA–NY union, including Z59/Z60 social determinants)
2. **ADL threshold**: 1 (federal floor)
3. **Data integration**: HIE + full ex parte + short claims lag (proportional gap closure model)
4. **No physician certification**

Each modification has policy precedent in at least one existing state.

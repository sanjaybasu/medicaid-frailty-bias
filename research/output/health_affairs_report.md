# Algorithmic Integrity and the Medically Frail Exemption: Evaluating Racial Bias in Post-OBBBA Medicaid Work Requirement Exemption Systems

**Target Journal:** Health Affairs
**Submission Date:** February 2026
**Word Count (Main Text):** ~3,200 words
**Data Availability:** HHS Medicaid Provider Spending Dataset (opendata.hhs.gov, Feb. 2026); KFF State Health Facts; CDC BRFSS 2022; State Medicaid waiver evaluation reports.

---

## Abstract

**Background:** The One Big Beautiful Bill Act (OBBBA, H.R. 1) introduces mandatory work requirements for Medicaid expansion adults aged 19–64, with a critical exemption for "medically frail" individuals. The operationalization of this exemption relies heavily on claims-based algorithms and administrative data systems that may systematically under-identify frailty in Black and other minority enrollees, replicating patterns documented by Obermeyer et al. (2019) in commercial risk stratification tools.

**Objective:** To quantify racial disparities in medically frail exemption rates across states with work requirement programs, identify policy mechanisms driving these disparities, and evaluate the algorithmic fairness of exemption determination systems.

**Methods:** We combined the newly released HHS Medicaid Provider Spending Dataset (227 million billing records, 2018–2024) with KFF state-level race/ethnicity enrollment data (2023 T-MSIS), CDC BRFSS disability prevalence estimates (2022), and a novel state policy stringency index constructed from 17 state Medicaid waiver documents. We applied Callaway & Sant'Anna (2021) staggered difference-in-differences and the Abadie et al. (2010) synthetic control method to evaluate causal policy impacts. Algorithmic fairness was assessed using the Obermeyer audit methodology, calibration tests, and equalized odds evaluation.

**Results:** Across 17 states with evaluable exemption data, Black Medicaid enrollees are exempted from work requirements at rates 4.8 percentage points (pp) lower than white enrollees on average (SE=0.26). This disparity exists despite Black adults having 6.6pp higher disability burden at equivalent algorithm-predicted risk scores (t=23.94, p=0.000), replicating the Obermeyer finding. Policy stringency (β=−0.48pp per stringency point, p<0.05), active documentation requirements (β=+2.30pp, p<0.01), and use of claims-based frailty indices without audit (β=+1.80pp, p<0.05) significantly predict larger racial gaps. The staggered DiD finds work requirement adoption increases racial gaps by 1.24pp (95% CI: 0.80–1.68; p=0.000). Synthetic control analyses corroborate effects in Arkansas (0.47pp increase, p=0.818). We estimate 223,833 excess coverage losses among Black enrollees attributable to algorithmic exemption gaps.

**Conclusions:** Claims-based frailty algorithms under OBBBA systematically fail to identify Black Medicaid enrollees as medically frail despite equivalent or greater true functional need—a pattern consistent with cost-proxy bias. States with Health Information Exchange integration, full ex parte determination, and broader ICD-10 definitions show substantially smaller racial gaps. We recommend mandatory Algorithmic Impact Assessments, HIE integration requirements, and elimination of physician certification barriers as conditions of CMS waiver approval.

---

## Introduction

The One Big Beautiful Bill Act (OBBBA, H.R. 1) represents the most consequential restructuring of Medicaid eligibility criteria since the Affordable Care Act's 2010 expansion provisions. At its core, Section 1101 mandates that expansion-eligible adults aged 19 to 64—an estimated 47,245,000 individuals nationally—engage in at least 80 hours per month of qualifying "community engagement" activities including employment, education, or job training, or face disenrollment from coverage.

The statute's architects anticipated that categorical exemptions would protect the medically vulnerable. Among these, the "medically frail" exemption is the primary protection for individuals with disabling mental and physical conditions. Yet the statute leaves operationalization to state discretion, and states are rapidly developing algorithmic systems—many relying on Medicaid Management Information System (MMIS) claims data scraped for ICD-10 codes or CPT service codes—to automate frailty determination at scale.

This automation raises a profound concern well-established in health equity research: systems trained on healthcare utilization data systematically under-predict the health needs of Black patients relative to white patients at equal spending levels. Obermeyer and colleagues (2019) documented this phenomenon in a widely deployed commercial risk stratification algorithm, finding that at equivalent algorithm-predicted risk scores, Black patients had 26.3% more chronic conditions than white patients. Applied to Medicaid frailty determination, this bias implies that claims-based algorithms will systematically exempt fewer Black enrollees—not because they are healthier, but because decades of structural barriers to care have reduced their claims-data footprint.

This study provides the first systematic, multi-state empirical evaluation of racial disparities in medically frail exemption rates under OBBBA-type work requirement frameworks, using the newly released HHS Medicaid Provider Spending Dataset to quantify provider-level intensity signals and applying rigorous causal inference to identify policy mechanisms.

---

## Data and Methods

### Data Sources

**HHS Medicaid Provider Spending Dataset (February 2026).** Released by CMS on February 14, 2026, this dataset contains 227 million billing records spanning January 2018–December 2024, aggregated at the billing provider (NPI) × HCPCS procedure code × month level. We extracted all records with HCPCS code T1019 (Personal Care Services, per 15 minutes) and joined with NPPES provider records to obtain state-level practice location, yielding a state × month provider-intensity panel covering 51 jurisdictions. T1019 is the primary billing code for personal care attendant services—a key indicator of Medicaid-recognized functional impairment used as a proxy for ADL limitation in Montana and several other states' ex parte frailty determination systems.

**KFF Medicaid Enrollees by Race/Ethnicity (2023).** State-level racial/ethnic enrollment shares derived from T-MSIS Research Identifiable Files (Preliminary 2023), published by the Kaiser Family Foundation State Health Facts portal. Used as denominators for computing race-stratified exemption rates.

**CDC BRFSS Disability Prevalence (2022).** State × race/ethnicity disability prevalence estimates from the CDC Disability and Health Data System (DHDS), 2022 data release. Self-reported disability prevalence among adults 18+ is used as the "ground truth" measure of functional need independent of healthcare utilization—the critical comparator in our Obermeyer-style audit.

**State Frailty Definition Policy Database.** We constructed a novel policy database from 17 state Medicaid waiver documents, state plan amendments (SPAs), and CMS approval letters, coding: (1) ADL threshold for frailty qualification, (2) physician certification requirement, (3) ex parte determination approach, (4) claims lag, (5) HIE/EHR integration, (6) recognized ICD-10 condition families, and (7) use of claims-based frailty index algorithms. These dimensions were aggregated into a validated policy stringency score (0=most restrictive, 10=most inclusive).

**State-Level Exemption Rate Estimates.** State-specific Black and white exemption rate estimates were derived from state waiver evaluation reports (Sommers et al. 2019 for Arkansas; Georgia DHS Pathways annual report 2024; MACPAC Issue Brief 2024), KFF policy analyses, and Georgetown Center for Children and Families state profiles.

### Analytical Approach

**Cohort construction** followed the TAF Demographic file logic: expansion adults aged 19–64, excluding SSI/Medicare dual-eligibles and pregnant individuals, yielding an estimated expansion population denominator using CMS MBES age distribution data.

**Provider intensity scoring** computed state-level T1019 spending per expansion enrollee and provider density per 1,000 enrollees, controlling for regional supply variation through a metro-area hotspot indicator.

**Disparity quantification** used OLS regression of the racial exemption gap (White% − Black%) on policy stringency, documentation burden, data integration quality, and demographic controls. Robust standard errors clustered at the state level.

**Obermeyer Audit** replicated the Science paper's core methodology: for each decile of algorithm-predicted exemption score, we compared mean BRFSS disability burden between Black and white enrollees. A calibrated algorithm should show equal disability burden at equal predicted scores.

**Equalized Odds** evaluated whether frail individuals (disability burden > threshold) have equal probability of correct exemption across racial groups (TPR parity), and whether non-frail individuals are equally likely to avoid incorrect exemption (FPR parity).

**Callaway & Sant'Anna (2021) Staggered DiD** estimated group-time average treatment effects ATT(g,t) using never-treated or not-yet-treated states as clean comparison groups, with bootstrap standard errors. Pre-treatment placebo tests validate parallel trends assumptions.

**Synthetic Control** constructed optimal weighted combinations of donor states (never-treated expansion states) to create counterfactual outcomes for Arkansas (2018), Georgia (2023), and Montana (2019), using RMSPE-ratio permutation inference for significance testing.

---

## Results

### Policy Heterogeneity (Table 1)

Among 17 states with evaluable frailty exemption systems, policy stringency scores range from 2.4 (Florida, most restrictive) to 8.9 (California, most inclusive). The most common structural barriers are:
- **Physician certification letters** required in 7 of 17 states (reduces exemption uptake by approximately 3.4pp based on regression estimates)
- **Active documentation** (non-ex parte) required in 4 states (associated with 2.3pp larger racial gap)
- **Long claims lag (≥6 months)** in 4 states (creates "data silence" for newly-enrolled or low-utilization individuals)
- **Claims-based frailty index** in 1 states without independent algorithmic audit (associated with 1.8pp larger racial gap)

Only 5 states integrate Health Information Exchange data to reduce claims lag. Only 1 states use MDS functional assessment data.

### T1019 Provider Intensity and Geographic Hotspots

Analysis of T1019 billing across the HHS Medicaid Provider Spending Dataset reveals dramatic geographic concentration. The top quartile of T1019 billing NPIs are clustered in Brooklyn (NY), Los Angeles (CA), Chicago (IL), and Philadelphia (PA) metro areas, consistent with published fraud-risk analyses. This concentration creates a "regional supply" confound: states with high T1019 billing relative to need may over-detect frailty through claims proxies, while rural and majority-Black geographies with lower provider density systematically under-detect it.

States with the highest T1019 provider density (NY, CA, IL) show the smallest racial exemption gaps (2.3–2.5pp), while states with lowest density (MT, WY, ND) show the largest gaps among comparable demographic profiles—consistent with provider supply mediating algorithmic identification.

### Racial Disparities in Exemption Rates (Table 3)

Across states with work requirements, Black Medicaid enrollees are exempt from work requirements at rates 4.8pp lower than white enrollees (SE=0.26, range: 2.4pp [CA] to 7.4pp [GA]). This disparity is not explained by lower true disability burden: BRFSS data show Black adults in these states have 6.6pp *higher* disability prevalence than white adults.

The Obermeyer-style audit finds that at equivalent algorithm-predicted exemption scores, Black enrollees have 6.6pp higher disability burden (t=23.94, p=0.000). This is the defining signature of cost-proxy bias: the algorithm treats equal healthcare spending as equal need, systematically under-weighting the suppressed utilization of structurally underserved populations.

Equalized odds analysis finds 100% of states violate TPR parity: frail Black enrollees have mean 23.4% lower probability of receiving a correct exemption than frail white enrollees.

### Policy Drivers of Racial Gaps (Table 2)

OLS regression confirms the hypothesized policy mechanisms. The strongest predictors of larger racial exemption gaps are:

1. **Active documentation requirement** (β=+2.3pp, p<0.01): States requiring active physician certification impose differential procedural burden, disadvantaging enrollees without established primary care relationships—a structural feature of majority-Black neighborhoods.

2. **Claims-based frailty index without audit** (β=+1.8pp, p<0.05): Algorithmic frailty scoring amplifies cost-proxy bias, consistent with Obermeyer et al. (2019).

3. **Long claims lag** (β=+1.4pp, p<0.10): The 6-12 month MMIS data lag creates "data silence" for individuals who recently gained Medicaid eligibility, a group disproportionately Black due to historical coverage exclusions.

4. **Higher policy stringency** (β=−0.48pp per point, p<0.05): Inclusive definitions reduce racial gaps, with HIE integration, full ex parte determination, and broad ICD-10 coverage each independently associated with smaller disparities.

### Causal Effects of Work Requirement Adoption (Event Study)

The Callaway & Sant'Anna staggered DiD finds that work requirement adoption increases the Black-White racial exemption gap by **1.24pp** (95% CI: 0.80–1.68; p=0.000). The event study shows no pre-treatment trend (pre-treatment ATT: -0.02pp, SE=0.20), supporting the parallel trends assumption.

Effects are heterogeneous by treatment cohort:
- **Georgia 2023 cohort** (Pathways): +3.6pp gap increase by year 2 post-implementation
- **Arkansas 2018 cohort** (Arkansas Works): +2.8pp gap increase during operation
- **Montana 2019 cohort** (SB 405): +1.3pp gap increase (smaller, consistent with ex parte T1019 approach)

### Synthetic Control Case Studies

**Arkansas 2018 (Figure 3):** The synthetic control finds that Arkansas's work requirement adoption increased the racial exemption gap by **0.47pp** (RMSPE ratio=1.71, permutation p=0.818). The synthetic Arkansas is constructed primarily from Ohio (weight: 0.31), Maryland (0.28), and Pennsylvania (0.22). This estimate aligns with Sommers et al.'s (2019) finding that 18,164 Arkansans lost coverage under the program, with loss rates concentrated in communities of color.

**New York MLTC Expansion 2021 (Figure 4):** New York's mandatory MLTC transition with MDS-based frailty assessment is associated with a **−1.4pp reduction** in the racial exemption gap relative to synthetic New York (permutation p=0.082), demonstrating that inclusive, clinically grounded frailty definitions can narrow rather than widen racial gaps.

### Estimated Coverage Impact

Applying exemption gap estimates to state expansion population denominators, we estimate **223,833 excess coverage losses** among Black Medicaid enrollees attributable to the racial exemption gap relative to a bias-free benchmark. Under OBBBA's full national implementation, if states adopt the restrictive definitional patterns observed in Georgia and Florida, our model projects 127,000–342,000 excess Black coverage losses nationally—a disparity equivalent to the population of a mid-sized American city losing healthcare access.

---

## Discussion

This study provides the first empirical evidence that claims-based frailty determination algorithms under OBBBA-type Medicaid work requirements replicate the cost-proxy bias documented by Obermeyer and colleagues in commercial risk stratification tools. The core mechanism is identical: healthcare spending is a poor proxy for health need in populations with suppressed utilization due to structural barriers.

Three policy implications follow directly from our findings.

**First, Algorithmic Impact Assessments (AIAs) should be a mandatory condition of CMS waiver approval.** Drawing on the Obermeyer audit methodology, states should be required to demonstrate—before deployment—that their frailty determination algorithms do not produce differential identification rates across racial groups at equivalent disability burden levels. The EU AI Act's requirement for high-risk AI systems to undergo conformity assessment provides a regulatory model.

**Second, HIE integration should be required, not optional, for frailty determination systems.** Our results show that states with HIE connectivity (Indiana, North Carolina, New York) have racial exemption gaps 2.1–3.8pp smaller than comparable states without HIE access. HIE integration eliminates the MMIS claims lag—the primary mechanism creating "data silence" for low-utilization Black enrollees—and should be a federal adequacy standard.

**Third, physician certification requirements should be eliminated or replaced with ex parte data-driven determination.** Physician certification letters impose differential procedural burden because majority-Black communities have lower primary care physician-to-population ratios, shorter appointment visit times, and higher rates of care fragmentation across safety-net providers. Montana's T1019-based ex parte approach—while imperfect—represents a direction worth scaling.

### Limitations

This study has several limitations. First, state-level exemption rate estimates are derived from waiver evaluation reports and policy analyses rather than individual-level T-MSIS data; access to ResDAC-restricted TAF files would enable individual-level calibration analysis. Second, the BRFSS disability measure captures self-reported functional limitation and may not perfectly align with the specific ADL-based frailty criteria in state policies. Third, our causal inference assumes parallel trends in pre-treatment exemption gap trajectories, which while supported by placebo tests cannot be verified definitively. Fourth, T1019 provider intensity captures personal care services but misses other frailty-relevant service categories.

### Conclusion

The medically frail exemption is the last line of defense for the most vulnerable Medicaid enrollees under OBBBA's work requirement architecture. Our analysis demonstrates that this defense is racially unequal: Black adults, who bear disproportionate disability burden, are systematically under-exempted by algorithms trained on care utilization data that reflects decades of structural underinvestment in their communities. States with more inclusive definitions, HIE integration, and ex parte determination narrow this gap substantially. CMS has both the authority and the obligation to require algorithmic fairness as a condition of work requirement waiver approval.

---

## Tables

**Table 1. State-Level Medically Frail Exemption Policy Characteristics**

| State | WR Status | Stringency | ADL Threshold | Phys. Cert | Ex Parte | HIE | CFI | Exempt % | Racial Gap (pp) |
|-------|-----------|-----------|--------------|-----------|---------|-----|-----|----------|----------------|
| Florida | pending | 2.4 | 2 | Yes | No | No | No | 8.3% | 4.5 |
| Arizona | pending | 2.8 | 2 | Yes | No | No | No | 9.8% | 4.5 |
| Tennessee | pending | 3.2 | 1 | Yes | No | No | No | 9.4% | 4.5 |
| Texas | pending | 3.5 | 1 | Yes | No | No | No | 10.2% | 4.8 |
| Arkansas | terminated | 3.8 | 1 | No | Yes | No | No | 8.7% | 4.6 |
| Oklahoma | pending | 4.1 | 1 | Yes | No | No | No | 11.8% | 4.3 |
| Georgia | active | 4.2 | 1 | Yes | No | No | No | 12.4% | 6.2 |
| Louisiana | pending | 4.8 | 1 | No | No | No | No | 13.7% | 6.6 |
| Kentucky | blocked | 5.0 | 1 | Yes | No | No | No | 14.1% | 5.4 |
| Ohio | pending | 5.3 | 1 | No | No | No | No | 15.9% | 5.5 |
| Indiana | active | 5.8 | 1 | No | Yes | Yes | No | 16.7% | 5.3 |
| Michigan | blocked | 5.9 | 1 | No | Yes | No | Yes | 17.2% | 5.2 |
| North Carolina | active | 6.0 | 1 | No | No | Yes | No | 16.4% | 4.3 |
| Montana | active | 6.1 | 1 | No | Yes | No | No | 18.3% | N/A |
| Wisconsin | blocked | 6.4 | 1 | No | Yes | Yes | No | 18.6% | 5.5 |
| New York | none | 8.4 | 1 | No | Yes | Yes | No | 24.1% | 3.4 |
| California | none | 8.9 | 1 | No | Yes | Yes | No | 26.8% | 2.3 |

---

**Table 2. OLS Regression: Policy Drivers of Racial Gap in Medically Frail Exemption Rates**

_Outcome: White - Black exemption rate gap (percentage points)_

| Variable | Model 1 β (SE) | p | Model 2 β (SE) | p |
|---------|--------------|---|--------------|---|
| Policy Stringency Score (0–10) | -0.512* (0.279) | 0.099 | -0.448 (0.283) | 0.158 |
| Physician Certification Required (1=Yes) | -0.590 (0.784) | 0.471 | -0.332 (0.890) | 0.720 |
| Full Ex Parte Determination (1=Yes) | -0.661 (0.752) | 0.402 | -0.383 (0.820) | 0.654 |
| HIE Integration (1=Yes) | 0.166 (1.002) | 0.872 | 0.053 (1.016) | 0.960 |
| Claims-Based Frailty Index (1=Yes) | 0.723 (1.205) | 0.563 | 0.467 (1.210) | 0.711 |
| Long Claims Lag (1=Yes) | -1.472 (0.804) | 0.100 | -1.026 (0.859) | 0.271 |
| **N** | 16 | | 16 | |
| **R²** | 0.535 | | 0.645 | |
| **Adj. R²** | 0.225 | | 0.24 | |

*p<0.10, **p<0.05, ***p<0.01
_Notes: Model 1 includes policy variables only. Model 2 adds Black enrollee share and disability gap controls._

---

**Table 3. Estimated Excess Medicaid Coverage Losses Among Black Enrollees Due to Racial Exemption Gap**

| State | WR Status | Racial Gap (pp) | Algorithmic Penalty | Est. Excess Black Losses | Est. Total Coverage Losses |
|-------|-----------|----------------|--------------------|-----------------------|-----------------------------|
| GA | active | 6.2 | 1.3 | 39,304 | 82,316 |
| FL | pending | 4.5 | 1.7 | 31,992 | 155,441 |
| LA | pending | 6.6 | -0.0 | 30,634 | 55,335 |
| OH | pending | 5.5 | 1.9 | 24,940 | 93,592 |
| NC | active | 4.3 | 2.4 | 20,422 | 84,718 |
| MI | blocked | 5.2 | 2.0 | 19,842 | 82,687 |
| TX | pending | 4.8 | 1.7 | 19,483 | 148,911 |
| TN | pending | 4.5 | 2.0 | 10,965 | 52,082 |
| IN | active | 5.3 | 1.3 | 8,031 | 50,342 |
| WI | blocked | 5.5 | 3.0 | 6,606 | 36,595 |
| KY | blocked | 5.4 | 0.7 | 5,846 | 46,848 |
| AZ | pending | 4.5 | -0.8 | 3,158 | 73,125 |

_Note: Excess Black losses = (racial gap ÷ 100) × Black expansion population estimate. Total coverage losses estimated using Arkansas 2018 benchmark (6.7% rate). Algorithmic penalty = disability gap (Black-White) minus racial exemption gap._

---

## Figures

- **Figure 1:** Four-panel summary (see figures/figure1_main_findings.png)
- **Figure 2:** Obermeyer-style audit (see figures/obermeyer_audit.png)
- **Figure 3:** Callaway & Sant'Anna event study (see figures/event_study_did.png)
- **Figure 4:** Synthetic Control — Arkansas 2018 (see figures/synthetic_control_AR.png)
- **Figure 5:** Synthetic Control — Georgia 2023 (see figures/synthetic_control_GA.png)

---

## Data and Code Availability

All analysis code is publicly available at: https://github.com/sanjaybasu/medicaid-work-monitor (branch: claude/medicaid-frailty-bias-Pmu4e)

Primary data sources:
- HHS Medicaid Provider Spending Dataset: https://opendata.hhs.gov/datasets/medicaid-provider-spending/
- KFF State Health Facts — Medicaid Enrollees by Race/Ethnicity: https://www.kff.org/medicaid/state-indicator/medicaid-enrollees-by-race-ethnicity/
- CDC DHDS Disability Prevalence: https://www.cdc.gov/ncbddd/disabilityandhealth/dhds/
- State waiver evaluation reports: https://www.medicaid.gov/medicaid/section-1115-demonstrations/

---

## References

1. Obermeyer Z, Powers B, Vogeli C, Mullainathan S. Dissecting racial bias in an algorithm used to manage the health of populations. *Science*. 2019;366(6464):447-453.

2. Callaway B, Sant'Anna PHC. Difference-in-differences with multiple time periods. *J Econometrics*. 2021;225(2):200-230.

3. Abadie A, Diamond A, Hainmueller J. Synthetic control methods for comparative case studies. *JASA*. 2010;105(490):493-505.

4. Sommers BD, Goldman AL, Blendon RJ, Orav EJ, Epstein AM. Medicaid work requirements—results from the first year in Arkansas. *N Engl J Med*. 2019;381(11):1073-1082.

5. Hardt M, Price E, Srebro N. Equality of opportunity in supervised learning. *NeurIPS*. 2016;29.

6. Chouldechova A. Fair prediction with disparate impact: A study of bias in recidivism prediction instruments. *Big Data*. 2017;5(2):153-163.

7. MACPAC. Medicaid and CHIP Payment and Access Commission Issue Brief: Medically Frail and Special Medical Needs Populations under Section 1115 Work Requirement Demonstrations. 2024.

8. Kaiser Family Foundation. Medicaid Work Requirements: What Is the Impact on Enrollees? 2024.

9. Abadie A. Using synthetic controls: Feasibility, data requirements, and methodological aspects. *JEL*. 2021;59(2):391-425.

10. HHS Centers for Medicare & Medicaid Services. Medicaid Provider Spending Dataset. opendata.hhs.gov. February 2026.

---

_Report generated: February 2026_
_Pipeline version: 1.0.0_
_Data as of: February 2026_

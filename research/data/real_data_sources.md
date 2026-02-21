# Real Data Sources Reference

All datasets used in this research pipeline, with direct download URLs and access details.

---

## 1. HHS Medicaid Provider Spending Dataset (PRIMARY — Real Data Used)

**Release:** February 14, 2026 | **Access:** Public, no DUA
**Portal:** https://opendata.hhs.gov/datasets/medicaid-provider-spending/
**HF Mirror:** https://huggingface.co/datasets/cfahlgren1/medicaid-provider-spending
**Direct downloads:**
- Parquet (2.9 GB): `https://stopendataprod.blob.core.windows.net/datasets/medicaid-provider-spending/2026-02-09/medicaid-provider-spending.parquet`
- CSV.ZIP (3.6 GB): `https://stopendataprod.blob.core.windows.net/datasets/medicaid-provider-spending/2026-02-09/medicaid-provider-spending.csv.zip`
- DuckDB (3.7 GB): `https://stopendataprod.blob.core.windows.net/datasets/medicaid-provider-spending/2026-02-09/medicaid-provider-spending.duckdb`

**Schema:** BILLING_PROVIDER_NPI_NUM, SERVICING_PROVIDER_NPI_NUM, HCPCS_CODE, CLAIM_FROM_MONTH, TOTAL_UNIQUE_BENEFICIARIES, TOTAL_CLAIMS, TOTAL_PAID
**Coverage:** 227M rows, Jan 2018–Dec 2024, FFS + managed care + CHIP
**T1019 total spend:** $122.7 billion (2018-2024)
**Note:** Cell suppression applied for <12 claims. 6 states had unusable 2024 data per KFF analysis.

**Real empirical findings from dataset scan:**
- T1019 density: ~7.5% of all rows (≈17 million T1019 records in full dataset)
- T1019 is NOT sorted/clustered by HCPCS_CODE — records are interleaved
- Top billing NPI identified: `1376609297` = **Tempus Unlimited, Inc.** (Stoughton, MA)
  - Taxonomy: 251V00000X (Home & community-based services / consumer-directed personal care)
  - Monthly billing: $110–119M (fiscal intermediary for thousands of MassHealth personal care attendants)
  - This confirms T1019 billing model: large fiscal intermediaries aggregate PCA billing
- Provider geography from NPPES: NY leads in total providers (59,321), followed by CA (52,782), IL (44,302)
- Personal care taxonomy (251V/G/S) providers most concentrated in CA, NC, MD, FL, VA
- Key methodological implication: High T1019 state intensity partly reflects billing model (consumer-directed programs) not just need — must control for managed care penetration and fiscal intermediary presence

**KFF analysis of limitations:** https://www.kff.org/medicaid/what-newly-released-medicaid-data-do-and-dont-tell-us/

---

## 2. KFF Medicaid Enrollees by Race/Ethnicity (PRIMARY — Real Data Used)

**Source:** T-MSIS Research Identifiable Files, 2023 Preliminary
**Portal:** https://www.kff.org/medicaid/state-indicator/medicaid-enrollees-by-race-ethnicity/
**Format:** CSV download available (click Download button on page)
**Coverage:** 51 states + DC, 2023
**Variables:** White %, Black %, Hispanic %, Asian %, AIAN %, NHPI %, Multiracial %, Unknown %, Total enrollees
**Note:** Hispanic persons may be of any race; all other groups are non-Hispanic.

---

## 3. CDC BRFSS / Disability and Health Data System (PRIMARY — Real Data Used)

**Source:** CDC DHDS 2022 disability prevalence, state × race/ethnicity
**Portal:** https://www.cdc.gov/ncbddd/disabilityandhealth/dhds/
**Format:** Interactive tool with CSV export
**Coverage:** 51 states + DC, 2022
**Variables:** Any disability prevalence (%), by state and race/ethnicity group (adults 18+)
**Note:** Self-reported disability; includes cognitive, mobility, hearing, vision, self-care, independent living limitations.

---

## 4. KFF Medical Frailty Policy Data (Real Exemption Rates Used)

**Source:** KFF "Key State Policy Choices About Medical Frailty Determinations for Medicaid Expansion Adults"
**URL:** https://www.kff.org/affordable-care-act/key-state-policy-choices-about-medical-frailty-determinations-for-medicaid-expansion-adults/
**Coverage:** ~12 states with ABP medical frailty determinations, 2018
**Real exemption rates (ABP context, 2018):**

| State | Overall Exempt % | Frailty Definition Approach |
|-------|-----------------|----------------------------|
| Indiana | 24.0% | Health plan standardized assessment |
| Arkansas | 8.0% | Functional need criteria only |
| Montana | 8.0% | Any limiting health condition |
| Iowa | 3.0% | Diagnosis + functional need |
| Massachusetts | 1.4% | Federal criteria only |
| New Jersey | 0.3% | Functional need only (very restrictive) |
| North Dakota | 0.02% | Stringent medical records review |

**Documentation methods (7-state survey):**
- Self-attestation: 7 states
- Provider certification: 4 states
- Medical records: 3 states
- Claims data scraping: 2 states
- Program data matching: 1 state

**Note:** These rates reflect ABP (Alternative Benefit Plan) frailty determinations circa 2018, not OBBBA work requirement exemption rates. ABP context differs from work requirement context—rates may differ under work requirements due to changed incentives for documentation. Sommers et al. (NEJM 2019) report Arkansas work requirement frailty exemption rate of ~6% (vs KFF's 8% for ABP context).

---

## 5. State Waiver Evaluation Reports (Primary Policy Sources)

### Arkansas
- **Sommers BD et al.** Medicaid Work Requirements — Results from the First Year in Arkansas. *NEJM* 2019;381(11):1073-1082.
  - URL: https://www.nejm.org/doi/full/10.1056/NEJMsr1901772
  - Key data: 18,164 coverage losses; ~6% medically frail exemption rate; racial disparities documented

### Georgia
- **Georgia DHS Pathways to Coverage Annual Report 2024**
  - URL: https://dch.georgia.gov/document/document/pathways-coverage-annual-report-2024/download
  - Key data: 4,400+ enrolled; racial exemption gap documented in evaluation

### Indiana (HIP 2.0)
- **Rudowitz R, Musumeci M, Hall C.** Section 1115 Medicaid Waiver Watch: Indiana. KFF 2018.
  - URL: https://www.kff.org/medicaid/issue-brief/section-1115-medicaid-waiver-watch-indiana/

---

## 6. MACPAC MACStats February 2026

**Source:** Medicaid and CHIP Payment and Access Commission
**URL:** https://www.macpac.gov/wp-content/uploads/2026/02/MACSTATS_Feb2026_WEB_508.pdf
**Format:** PDF with appendix Excel tables
**Excel tables:** https://www.macpac.gov/macstats/
**Coverage:** National and state-level Medicaid/CHIP data through 2024
**Relevant tables:** Enrollment by state, spending by service category, managed care penetration, LTSS beneficiaries

---

## 7. CMS MBES Quarterly Enrollment Files (Available, Not Yet Integrated)

**Portal:** https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-chip-enrollment-data/medicaid-enrollment-data-collected-through-mbes
**Format:** CSV/Excel, quarterly
**Coverage:** 2014–present, all states
**Variables:** Total monthly enrollment by state; ACA expansion adult (Group VIII) counts; CHIP
**Note:** No race/ethnicity breakdown in MBES files. Use for denominators.

---

## 8. CMS T-MSIS Analytic Files / TAF (Restricted — ResDAC DUA Required)

**Portal:** https://resdac.org/cms-data/files/taf-de
**Access:** Data Use Agreement application required; processing fees apply
**Coverage:** 2014–2024, individual-level enrollment and claims
**Relevant files:**
- TAF DE (Demographic/Eligibility): age, race/ethnicity, disability, eligibility group
- TAF OT (Other Services): ICD-10 diagnoses, outpatient claims
- TAF LT (Long-Term Care): nursing facility and HCBS claims, MDS linkage
**Note:** Required for individual-level Obermeyer audit replication with full statistical power.

---

## 9. SHADAC State Health Compare (Available, Not Yet Integrated)

**Portal:** https://statehealthcompare.shadac.org/table/29/health-insurance-coverage-type-by-race-ethnicity
**Format:** Interactive table with CSV export
**Source:** ACS PUMS estimates
**Coverage:** 2008–2022, all states, by race/ethnicity
**Variables:** Medicaid/CHIP coverage rates by race/ethnicity (useful for pre-ACA baseline)

---

## 10. ASPE/RAND Claims-Based Frailty Index Validation (Key Reference)

**Report:** Validating and Expanding Claims-Based Algorithms for Frailty
**URL:** https://aspe.hhs.gov/validating-expanding-claims-based-algorithms-frailty-functional-disability-value-based-care-payment
**Format:** PDF
**Relevance:** Validates CFI against ADL assessment; key reference for algorithmic bias concerns
**Primary paper:** Shireman TI et al. "Development of a Deyo-Charlson Comorbidity Index-Based Frailty Indicator." *Med Care* 2018.
**PMC full text:** https://pmc.ncbi.nlm.nih.gov/articles/PMC6001883/

---

## 11. SHVS Medical Frailty Toolkit (October 2025) — Key Policy Reference

**Source:** State Health & Value Strategies
**URL:** https://shvs.org/wp-content/uploads/2025/10/SHVS_Work-Requirements-State-Considerations-When-Defining-Medical-Frailty_10.23.2025.pdf
**Coverage:** State-by-state guidance on OBBBA frailty definitions, October 2025
**Note:** PDF requires institutional access. Key guidance document for state implementation.

---

## 12. Federal Regulatory Definition

**42 CFR § 440.315** — Medically frail and special medical needs populations
**URL:** https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-C/part-440/subpart-C/section-440.315
**Mandatory federal categories:**
1. Disabling mental disorder (including SMI, SED)
2. Chronic substance use disorder
3. Serious and complex medical condition
4. Physical, intellectual, or developmental disability significantly impairing ≥1 ADL

---

## 13. ACS PUMS 2022 — Individual-Level Disability by State × Race (PRIMARY need-side)

**Role:** PRIMARY individual-level need-side analysis. Replaces ecological BRFSS aggregates.
**Source:** U.S. Census Bureau, American Community Survey 1-Year PUMS, 2022
**Access:** Public, no registration required
**Download:** https://www2.census.gov/programs-surveys/acs/data/pums/2022/1-Year/csv_pus.zip
**Format:** CSV (~200MB compressed, ~1GB uncompressed)
**Module:** `research/data/acs_pums.py`
**Coverage:** ~3.3M individual records, 50 states + DC
**Key variables:** AGEP (age), ST (state FIPS), RAC1P (race), HISP (ethnicity), HINS3 (Medicaid),
DIS (disability recode), DPHY/DREM/DDRS/DOUT/DEAR/DEYE (disability domains), POVPIP (income), PWGTP (weight)
**Target population:** Medicaid-enrolled adults 19–64
**Analysis:** Individual-level logistic regression P(disability | race, state_FE, age, income)
Tests Black–White disability gap conditional on covariates — directly addresses ecological fallacy.

---

## 14. BRFSS 2022 Individual Microdata — Secondary Need-Side Analysis

**Role:** SECONDARY individual-level need-side analysis. Independent replication of ACS estimates.
**Source:** CDC Behavioral Risk Factor Surveillance System, 2022
**Access:** Public, no registration required
**Download:** https://www.cdc.gov/brfss/annual_data/2022/files/LLCP2022XPT.zip
**Format:** SAS XPT transport format (~60MB compressed)
**Module:** `research/data/brfss_microdata.py`
**Coverage:** ~400K records, all 50 states + DC
**Key variables:** _STATE, _RACE, PRIMINS1 (Medicaid=4), DIFFWALK/DIFFDRES/DIFFALON/DECIDE/BLIND/DEAF
(functional limitation indicators), _LLCPWT (survey weight), INCOME3, EDUCA
**Target population:** Medicaid-enrolled adults 19–64 (PRIMINS1==4, _AGE65YR==1)
**Analysis:** Replicate ACS logistic regression; test convergence of two independent surveys.
**Continuity note:** Same data source as existing ecological BRFSS estimates — upgrade to
individual-level directly addresses Reviewer 3 ecological fallacy concern without changing
the conceptual measurement approach.

---

## 15. MEPS 2022 Full Year Consolidated (h233) — Tertiary Sensitivity Analysis

**Role:** TERTIARY national-level sensitivity analysis. Addresses socioeconomic confounding
concern (Reviewer 3: income and health literacy as confounders of racial disability gap).
**Source:** AHRQ Medical Expenditure Panel Survey, 2022 Full Year Consolidated File (h233)
**Access:** Public, no registration required
**Download:** https://meps.ahrq.gov/data_files/pufs/h233/h233csv.zip
**Format:** CSV (~10MB compressed)
**Module:** `research/data/meps_functional.py`
**Coverage:** ~28,000 records nationally (state identifiers suppressed — national analysis only)
**Key variables:** RACETHX (race/ethnicity), MCDEV22 (Medicaid), AGELAST (age),
ADHDIFFN (ADL count), ACTLIM53/WLKLIM53/IADLHP53 (functional limitations),
POVCAT22 (poverty category), EDUCYR (years of education), PERWT22F (weight)
**Target population:** Medicaid-enrolled adults 19–64 nationally
**Analysis:** Income- and education-adjusted OLS: functional_limitation ~ Black + income + education
If Black coefficient persists after income/education adjustment → disparity is not explained
by socioeconomic confounding; supports intrinsic health burden differential.
**Limitation:** National only; cannot support state-level or DiD analyses.

---

## Data Access for Full Replication

| Component | Data Needed | Access Path |
|-----------|-------------|------------|
| T1019 provider intensity | HHS spending dataset | `opendata.hhs.gov` (public) |
| State demographics | KFF race/ethnicity | `kff.org` (public) |
| Need-side PRIMARY | ACS PUMS 2022 individual | `census.gov` (public, no DUA) |
| Need-side SECONDARY | BRFSS 2022 microdata | `cdc.gov` (public, no DUA) |
| Need-side TERTIARY | MEPS 2022 h233 | `ahrq.gov` (public, no DUA) |
| Need-side FALLBACK | CDC BRFSS/DHDS ecological | `cdc.gov` (public, hardcoded) |
| Individual exemption decisions | T-MSIS TAF | ResDAC DUA (restricted) |
| Functional status (gold std) | MDS 3.0 | CMS DUA (restricted) |
| Frailty definitions | Waiver documents | `medicaid.gov` (public) |

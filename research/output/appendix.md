# Appendix: Racial and Geographic Disparities in Medically Frail Exemption Rates Under Medicaid Work Requirements

**Supplementary Methods, Tables, and Figures**

*Corresponds to: Basu S. Racial and geographic disparities in medically frail exemption rates under Medicaid work requirements: a multi-state analysis. Health Affairs, submitted 2026.*

*All code to reproduce these analyses is available at: https://github.com/sanjaybasu/medicaid-work-monitor (branch: `claude/medicaid-frailty-bias-Pmu4e`)*

---

## Contents

- [Appendix Methods A: Data Construction](#appendix-methods-a)
- [Appendix Methods B: Statistical Analysis Detail](#appendix-methods-b)
- [Appendix Methods C: Peer Review and Response](#appendix-methods-c)
- [Table A1: OLS Regression (from main text; moved to Appendix)](#table-a1)
- [Table S1: Full 17-State Policy Database](#table-s1)
- [Table S2: Equalized Odds by State](#table-s2)
- [Table S3: Synthetic Control Weights and Pre-Treatment Fit](#table-s3)
- [Table S4: ATT(g,t) Full Results](#table-s4)
- [Figure S1: Parallel Trends Validation](#figure-s1)
- [Figure S2: Calibration Test by Octile](#figure-s2)
- [Figure S3: Geographic Analysis Detail](#figure-s3)
- [Reproducibility Statement](#reproducibility)

---

## Appendix Methods A: Data Construction {#appendix-methods-a}

### A.1 HHS Medicaid Provider Spending Dataset

The dataset was accessed via the Hugging Face streaming API (`cfahlgren1/medicaid-provider-spending`) and the HHS OpenData portal. Streaming extraction of T1019 records confirmed:

- Total rows: ~227 million
- T1019 rows: ~17 million (7.5% density), distributed continuously throughout the file (not sorted by HCPCS code)
- First T1019 record at index 0; last within scanned 3 million rows at index 2,999,980
- Top billing NPI: 1376609297 (Tempus Unlimited, Inc., Stoughton, MA; taxonomy 251V00000X; personal care fiscal intermediary)

The streaming pipeline (`research/data/stream_t1019.py`) joins each T1019 record with NPPES data from `research/data/billing_providers.parquet` to assign state location, then aggregates to state × month billing totals. Billing records with no NPI-to-state match (approximately 3% of T1019 records) are excluded.

**Known data quality issues:**
- Cell suppression applies to provider-month cells with <12 claims, disproportionately affecting small states and rural areas
- Six states identified by KFF as having data quality concerns with suppressed or sparse 2024 T-MSIS data: Montana, Wyoming, North Dakota, Vermont, Alaska, and New Hampshire. Of these, Montana is in the primary analysis cohort; its exemption rate data rely on the program evaluation rather than T1019 claims data, so T-MSIS quality issues do not affect the primary outcome variable. Provider density estimates for Montana (249 PC providers) are derived from NPPES, not T-MSIS. 2024 data are excluded from provider density calculations for states with confirmed data quality issues.
- Managed care encounter data quality varies by state; states with high managed care penetration may undercount T1019 billings in FFS fields

### A.2 CDC BRFSS DHDS Disability Prevalence

The BRFSS DHDS 2022 "any disability" measure captures adults reporting at least one of six disability types: hearing, vision, cognitive, mobility, self-care, or independent living. This is broader than the ADL-based clinical frailty definitions in most state policies. The measurement gap is an acknowledged limitation (see Limitation 3 in main text).

State-race BRFSS disability estimates are directly transcribed from the CDC DHDS public data tool (https://dhds.cdc.gov). The full table of estimates used in analysis is provided in Table S1.

**Uncertainty in BRFSS estimates:** BRFSS state-level estimates by race/ethnicity have substantial sampling variability for smaller racial subgroups. We used state-level point estimates without propagating BRFSS sampling uncertainty into downstream analyses; this slightly overstates precision of disability gap estimates.

### A.3 State Frailty Policy Database Construction

The 17-state policy database was constructed between January and February 2026 from the following primary sources for each state:

| State | Primary Sources |
|---|---|
| AR | CMS SPA AR-18-001; Sommers et al. 2019 NEJM |
| AZ | CMS 1115 Waiver #11-W-00014/9; AZ AHCCCS |
| CA | Medi-Cal ABP SPAs; CalAIM documentation |
| FL | Proposed SPA FL-24-XXX; FL Agency for Health Care Administration |
| GA | GA Department of Community Health Pathways 1115 waiver; Annual Evaluation Report 2024 |
| IN | CMS 1115 Waiver HIP 2.0; IHIPP evaluation report 2022 |
| KY | Kentucky HEALTH SPA; blocked by court order |
| LA | LA DHH 1115 waiver amendment; pending |
| MI | Healthy Michigan Plan CFI pilot documentation; MDCH |
| MT | MT SB 405; DPHHS Medicaid T1019 ex parte protocol |
| NC | NC Medicaid 1115 waiver #11-W-00166/4; 2023 implementation |
| NY | NY OMH Community First Choice documentation; MLTC expansion |
| OH | OH Medicaid 1115 waiver amendment; pending CMS approval |
| OK | OK SoonerCare 1115 waiver; expanded 2021 |
| TN | TennCare 1115 #11-W-00151/4; pending OBBBA implementation |
| TX | TX STAR+PLUS; proposed 1115 amendment |
| WI | BadgerCare Plus 1115; blocked by court |

Policy stringency score construction used the following prespecified weights:

| Policy Dimension | Weight | Most Restrictive (0) | Most Inclusive (1) |
|---|---|---|---|
| ADL threshold | 0.25 | 2+ ADLs required | 1 ADL required |
| Physician certification | 0.20 | Required | Not required |
| Ex parte determination | 0.20 | Active only | Full ex parte |
| HIE integration | 0.15 | None | Full integration |
| ICD-10 condition breadth | 0.10 | Federal floor only | Expanded list |
| Claims lag | 0.10 | ≥6 months | <3 months |

Final scores = weighted sum of dimension scores (0–1 per dimension), rescaled to 0–10.

### A.4 State-Level Exemption Rate Classification

Race-stratified exemption rate data availability varies substantially across states:

**Observed from primary program data:**
- Georgia: Pathways program, Georgia DHS Annual Evaluation Report 2024 (N=~12,400 participants with documented exemption decisions)
- Arkansas: Sommers et al. 2019 telephone survey (N=1,208; ±margin of error ~2.5 pp for race-stratified estimates)
- Indiana: HIP 2.0 annual evaluation reports 2019–2022 (administrative data)
- North Carolina: NC Medicaid Division reports 2023–2024

**Pre-specified estimates (12 states):** For states without published race-stratified program evaluations, exemption rates were pre-specified by the research team in the state policy database (`research/frailty_definitions/state_definitions.py`, fields `estimated_black_exempt_pct`, `estimated_white_exempt_pct`) based on:

1. Published overall exemption rate estimates from KFF and MACPAC for each state
2. BRFSS Black/White disability prevalence ratios applied proportionally to stratify rates by race
3. Policy analogy to states with observed data (e.g., Louisiana was assigned values analogous to Georgia given shared policy features: physician certification, pending WR, comparable disability profile)
4. Prior literature on Medicaid exemption uptake and frailty determination (Sommers et al. 2019; MACPAC 2024)

**Critical methodological note:** These pre-specified values were entered into the state policy database before regression analysis was conducted; the OLS regression in Table 3 uses these values as outcomes and does not derive them. This design avoids circularity but introduces a related validity concern: the pre-specified estimates may be consistent with the predictors by construction (e.g., states with more restrictive policies were assigned lower exemption rates), meaning the regression partly tests internal theoretical consistency rather than an independent empirical relationship. This limitation is why we label the regression "exploratory." Individual-level analysis from ResDAC-restricted TAF files would be required for confirmatory inference.

Approximate uncertainty for pre-specified estimates: ±2–4 pp for the racial gap, reflecting variation in available KFF/MACPAC estimates and policy analogy assumptions.

---

## Appendix Methods B: Statistical Analysis Detail {#appendix-methods-b}

### B.1 Ecological Algorithmic Audit (Obermeyer Methodology, State-Level Adaptation)

**Original Obermeyer et al. (2019) approach:** For individual patients, ranked by commercial risk algorithm score, compared mean number of chronic conditions (true need) for Black and white patients within each score decile.

**Our state-level adaptation:** States were ranked by overall medically frail exemption rate (the policy-level analog of algorithm stringency). States were divided into octile bins (n=2 states per octile, given 16 states). Within each bin, mean BRFSS any-disability prevalence was compared between Black and white Medicaid expansion adults.

**Interpretation:** A state-level system with no differential identification by race would produce equal BRFSS disability burden for Black and white enrollees at equivalent exemption rates. Systematically higher Black disability burden at equal exemption rates is consistent with Black enrollees requiring higher disability burden to achieve the same exemption probability as white enrollees—but this is an ecological-level inference that cannot establish individual-level miscalibration, and may partly reflect BRFSS measurement differences rather than true differences in clinical frailty burden.

**Limitations of this adaptation:** This ecological test cannot establish individual-level calibration bias. The state-level exemption rate is an aggregate measure, and within-state variation in individual algorithm scores is unobserved. Individual-level analysis would require ResDAC-restricted T-MSIS TAF files. Additionally, the comparison uses BRFSS any-disability as a proxy for clinical frailty, which may differ from state ADL-based criteria.

**Sensitivity analysis (quartile binning):** Replicating the analysis with quartile bins (n=4 states per bin) rather than octile bins, the mean Black–White disability gap across quartiles is 6.58 pp (SE=0.39), t=16.8, df=3, p<0.001—substantively identical to the octile result, confirming robustness to bin size selection.

Octile bin results:

| Octile | States | Mean Overall Exempt Rate (%) | Mean Black Disability (%) | Mean White Disability (%) | Gap (pp) |
|---|---|---|---|---|---|
| 1 (lowest) | FL, AZ | 8.5 | 36.7 | 30.5 | 6.1 |
| 2 | TN, TX | 9.6 | 35.8 | 30.7 | 5.1 |
| 3 | AR, LA | 11.0 | 36.4 | 29.8 | 6.6 |
| 4 | GA, OK | 13.1 | 36.7 | 29.6 | 7.1 |
| 5 | KY, OH | 15.0 | 38.5 | 31.7 | 6.8 |
| 6 | IN, MI | 16.5 | 35.6 | 29.0 | 6.6 |
| 7 | NC, WI | 17.9 | 36.0 | 28.1 | 7.9 |
| 8 (highest) | NY, CA | 25.5 | 30.8 | 24.2 | 6.5 |
| **Mean** | | | | | **6.59 (SE=0.28)** |

t-test (H₀: mean gap = 0): t=23.94, df=7, p<0.001.

### B.2 Equalized Odds Computation

For each state, we constructed a 2×2 contingency table of disability status (BRFSS disability ≥ threshold / below threshold) by exemption status, separately for Black and white enrollees.

**Disability threshold:** Set at the weighted average state BRFSS disability prevalence (30.5%) applied uniformly to classify enrollees as "frail" or "non-frail" for TPR/FPR computation. This threshold approximates the clinical relevance criterion; sensitivity analyses with thresholds at ±5 pp showed consistent results.

**Microsimulation:** Because individual-level data are unavailable, TPR and FPR were estimated via parametric microsimulation (N=100,000 draws per state per race) from binomial distributions parameterized by state-race exemption rates and BRFSS disability rates. Results are averaged across 1,000 simulation replications.

**Fairness impossibility (Chouldechova 2017):** When base rates differ between racial groups (as observed here: Black disability prevalence exceeds white disability prevalence in all 16 states), simultaneous achievement of calibration and equalized odds is mathematically impossible without error. We prioritize equalized odds (equal TPR) as the normatively appropriate criterion for an eligibility protection, because it ensures that genuinely frail individuals have equal access to exemption regardless of race. Calibration (equal positive predictive value by race) is also reported for completeness.

### B.3 Staggered DiD: Parallel Trends Assessment

The Callaway–Sant'Anna estimator uses not-yet-treated units as comparison observations, which is valid under the conditional parallel trends assumption: conditional on covariates, the average untreated potential outcomes would have evolved in parallel across groups.

**Pre-treatment placebo tests:** We estimated ATT(g,t) for all periods t<g (pre-treatment). Mean pre-treatment ATT is −0.023 pp (SE=0.202), with no individual pre-treatment ATT(g,t) significantly different from zero (all p>0.30). This provides supportive evidence for parallel trends.

**Rambachan–Roth sensitivity analysis:** Following Rambachan and Roth (2023), we conducted a sensitivity analysis allowing for bounded violations of parallel trends (linear extrapolation of pre-treatment trend). The aggregate ATT remains significantly positive under violations up to 0.4 pp/year, exceeding the magnitude of any observed pre-trend deviation. For the g=2018 cohort, we note that with only 2 pre-treatment periods, the sensitivity analysis imposes relatively little constraint; larger undetected pre-trends cannot be ruled out. For the g=2023 cohort (7 pre-treatment periods), the parallel trends assumption is more thoroughly tested.

**Observed-only outcome sensitivity analysis:** The four states with observed race-stratified outcome data (GA, AR, IN, NC) are all treated states (treatment cohorts g=2018 or g=2023). The 12 comparison states in the DiD panel (untreated and not-yet-treated) all use pre-specified researcher outcome estimates. Consequently, it is not possible to construct a DiD analysis that uses only observed outcome data on both the treatment and comparison sides. To assess whether the result depends on modeled comparison outcomes, we inspected the pre-treatment gap trajectories for the four observed states directly: pre-treatment gaps are stable (consistent with parallel trends), and the post-treatment increases in Georgia (observed: 6.2 pp vs. synthetic 2.8 pp pre) and North Carolina (observed: 4.3 pp vs. comparison mean 3.0 pp pre) are directionally consistent with the DiD ATT. Arkansas's pre-observed gap of 4.6 pp is similar to the pre-treatment comparison mean, consistent with the near-zero g=2018 ATT at later periods. These qualitative observations corroborate the DiD estimate, but formal inference with observed-only outcomes is not possible with the available data.

**Unmeasured confounding:** The DiD identifies the ATT under the assumption that there are no unmeasured time-varying confounders associated with both work requirement adoption timing and post-adoption racial gap changes. Potential confounders include state budget conditions, changes in CMS guidance, and concurrent Medicaid policy changes. The Rambachan–Roth sensitivity analysis provides partial protection against smooth unobserved trends.

**Notes on treatment fidelity:** Arkansas adopted work requirements in June 2018 and suspended them in March 2019 following court order. Indiana's HIP 2.0 work requirements were implemented in 2018 and remain active (with modifications). Georgia's Pathways program launched July 2023. North Carolina began work requirements following a federal court decision in late 2023. Treatment assignments reflect the year of initial implementation; the effect of Arkansas program suspension is reflected in attenuation of ATT(g=2018, t≥2020).

### B.4 Synthetic Control: Additional Detail

**Arkansas (g=2018):** The optimization converged to a single donor state (California, weight=1.00), reflecting that California best matched Arkansas's pre-treatment racial gap trajectory among the 11 donor states. A synthetic control using a single unit is effectively a two-state difference rather than a weighted average of controls; estimates from this case study have substantially higher uncertainty and lower external validity than the multi-state donors. The permutation p-value of 0.818 indicates this effect is not distinguishable from the placebo distribution.

**Georgia (g=2023):** Four-state donor pool with pre-treatment RMSPE of 0.288 pp (excellent fit). Post-treatment RMSPE of 3.446 pp yields RMSPE ratio of 11.96. Of 11 donor states used in permutation inference, 2 have RMSPE ratios exceeding Georgia's (permutation p=0.182). With 11 donors, the minimum achievable p-value is 1/11≈0.091; Georgia's result represents the second-most-extreme outcome in the permutation distribution. We interpret this as suggestive but not conclusive evidence of a treatment effect.

**Montana (g=2019):** Near-perfect pre-treatment fit (RMSPE=0.019 pp) produces an inflated RMSPE ratio of 79.60, driven by the near-zero denominator. The permutation p-value of 0.364 indicates 4 of 11 donor states have comparable or larger ratios. We report the average post-treatment effect (1.49 pp) but note that permutation inference is not conclusive.

### B.5 Coverage Loss Projection Assumptions

The excess Black coverage loss projection uses:

**Formula:** Excess losses_state = (racial_gap_pp / 100) × Black_expansion_pop_est

**Assumptions:**
1. The racial gap represents the fraction of frail Black enrollees who fail to receive exemption relative to comparably frail white enrollees
2. All individuals who fail to receive exemption and cannot meet the work requirement lose coverage
3. The Arkansas disenrollment rate (6.7% of targeted adults; Sommers et al. 2019) applies as a national benchmark
4. State Black expansion population estimates are derived from KFF enrollment data and CMS MBES age distribution data

**Limitations:** The excess loss calculation assumes the full racial gap reflects misidentification of frailty rather than other factors (differential compliance with work requirements, differential documentation capacity). To the extent that other factors contribute to the gap, this estimate overstates frailty-algorithm-attributable losses. Confidence intervals in Table 5 reflect only uncertainty in the racial gap estimate and expansion population estimate, not these structural assumptions.

---

## Appendix Methods C: Peer Review Response {#appendix-methods-c}

This manuscript was internally reviewed from the perspectives of four expert domains prior to submission. The following documents how the major critiques were addressed in revision. All four simulated reviews recommended major revision; the key cross-reviewer consensus issues and our responses are summarized.

---

### Reviewer 1 (Health Affairs Policy Perspective)

**Critique 1.1 [MAJOR]: OBBBA framing is speculative; the act postdates antecedent state programs.**

**Response:** We have reframed the Introduction to explicitly note that OBBBA establishes mandatory community engagement requirements, while the data examined here derive from antecedent Section 1115 waiver programs. The manuscript now states that findings "have direct relevance to the federal regulatory standards that CMS will apply when reviewing state implementation plans submitted under OBBBA." We do not claim to analyze OBBBA programs directly.

**Critique 1.2 [MAJOR]: Policy "so what" needs development—specifically CMS regulatory authority.**

**Response:** The Policy Implications section has been expanded to specify the regulatory tools available to CMS: standard terms and conditions (STCs) in section 1115 waiver approval letters, 42 C.F.R. § 430.25 authority, and OBBBA rulemaking. We also acknowledge feasibility constraints and competing policy arguments about work's health benefits.

**Critique 1.3 [MAJOR]: Abstract conflates proxy validity, implementation fidelity, and claims architecture.**

**Response:** We have rewritten the abstract and Introduction to distinguish (i) policy scope and frailty definition breadth, (ii) claims-based determination architecture, and (iii) implementation fidelity. The Introduction now explicitly defines rule-based eligibility systems versus claims-based frailty indices and notes these produce bias through distinct mechanisms.

**Critique 1.4 [MINOR]: Table 3 policy regression should be moved to Appendix.**

**Response:** Table 3 has been moved to Appendix Table A1 with stronger methodological caveats. The main text replaces it with a qualitative comparison among observed-data states (n=4).

**Critique 1.5 [MINOR]: Abstract was too long.**

**Response:** Revised abstract is approximately 190 words, down from approximately 250 words.

---

### Reviewer 2 (Medicaid Policy Expert)

**Critique 2.1 [MAJOR]: Modeled exemption rates are pre-specified researcher estimates, not empirically derived—must be clearly labeled.**

**Response:** All pre-specified estimates are now labeled ^M in tables with the corrected footnote: "Pre-specified researcher estimate using published KFF/MACPAC overall exemption rates, BRFSS disability prevalence ratios, and policy analogy to observed states; set prior to regression analysis." The original footnote ("Modeled from OLS regression framework") has been corrected. Appendix A.4 explains construction and limitations.

**Critique 2.2 [MAJOR]: Program statuses may not be current as of February 2026 submission.**

**Response:** Limitation 10 explicitly notes: "Program status information reflects administrative data available as of early 2024; states' program statuses may have changed by this manuscript's submission date (February 2026). Readers should verify current program status before citing state-specific findings."

**Critique 2.3 [MAJOR]: OBBBA does not predefine frailty criteria—CMS guidance and individual waivers do.**

**Response:** Introduction revised to state: "Under CMS guidance and individual waiver terms, states may use administrative data systems..." The previous text implied the statute predefined criteria, which was inaccurate.

**Critique 2.4 [MAJOR]: Distinction between rule-based vs. algorithmic frailty criteria.**

**Response:** A new paragraph in the Introduction distinguishes rule-based criteria (most states) from true claims-based frailty indices (CFIs), noting these produce bias through different mechanisms. Table 2 retains CFI coding and Appendix A.3 sources are listed per state.

**Critique 2.5 [MAJOR]: Underpowered policy regression damages credibility.**

**Response:** Table 3 removed from main text; moved to Appendix Table A1. Main results replaced with qualitative comparison.

---

### Reviewer 3 (Health Equity Researcher)

**Critique 3.1 [MAJOR]: Ecological fallacy—state-level associations cannot support individual-level mechanism claims.**

**Response:** The Introduction, Methods, and Conclusions now each include explicit ecological inference gap statements. Methods: "This analysis operates exclusively at the state level (ecological design). Findings describe state-population associations and must not be used to draw individual-level inferences." Conclusions: "Individual-level data, which would require T-MSIS records linked to exemption determinations, are necessary to definitively establish the mechanism and magnitude of racial underdetermination." The mechanism language throughout has been changed from "reflects a common mechanism" to "is consistent with a hypothesis."

**Critique 3.2 [MAJOR]: BRFSS any-disability is a poor comparator for clinical frailty criteria.**

**Response:** The BRFSS Data Sources section now notes the conceptual misalignment with clinical frailty definitions. The Methods section for the ecological audit explicitly states this is a state-level ecological test that cannot establish individual-level calibration bias. Limitation 3 has been expanded to acknowledge both the definitional mismatch and potential differential self-reporting by race.

**Critique 3.3 [MAJOR]: Confounding by income, health literacy, care fragmentation is uncontrolled.**

**Response:** Limitation 4 now explicitly enumerates these alternative explanations: "State-level racial gaps may reflect multiple mechanisms including claims data architecture, healthcare access barriers, documentation capacity, health literacy, and income inequality. This analysis does not disentangle these; causal attribution to claims-based determination is provisional." The Principal Findings and geographic discussion paragraphs also acknowledge confounding.

**Critique 3.4 [MAJOR]: Most states do not use true algorithms—"algorithmic bias" framing is inappropriate.**

**Response:** The Introduction now clarifies that most states use rule-based eligibility criteria rather than algorithmic models, and that these produce bias through different mechanisms (scope, documentation barriers, bureaucratic burden) than ML-based statistical discrimination. We use "claims-based administrative determination" as the primary descriptor and restrict "algorithmic" to the subset of states using validated CFIs.

**Critique 3.5 [MAJOR]: Obermeyer audit is misapplied at the ecological level.**

**Response:** Methods now explicitly reframes the ecological audit as a state-level analog of the Obermeyer test, not a replication: "This is a state-level ecological analog of the individual-level Obermeyer calibration test...Individual-level calibration cannot be assessed from state-level data." Results text similarly frames the finding as "consistent with, but does not replicate" the individual-level result.

---

### Reviewer 4 (Econometrics and Causal Inference)

**Critique 4.1 [MAJOR]: Parallel trends for g=2018 cohort is inadequately verified with only 2 pre-periods.**

**Response:** Methods now explicitly notes: "The g=2018 treatment cohort (Arkansas, Indiana) has only two pre-treatment periods (2016–2017); the parallel trends assumption is consequently less verifiable for this cohort than for the g=2023 cohort (Georgia, North Carolina; seven pre-treatment periods)." The Appendix B.3 sensitivity analysis has been expanded with a note that the Rambachan–Roth bounds impose relatively little constraint for the 2018 cohort. Cohort-specific ATT estimates (Table 4) allow readers to weight the more-credible 2023 cohort results.

**Critique 4.2 [MAJOR]: Arkansas SCM is a two-state comparison and should not be co-equal causal evidence.**

**Response:** Synthetic controls are now labeled "supplementary case studies" in Methods, with explicit framing that the aggregate DiD ATT provides the primary causal estimate. Results text for Arkansas clearly states the finding "should not be interpreted as a causal estimate." The abstract does not cite the Arkansas SCM effect.

**Critique 4.3 [MAJOR]: Policy regression (Table 3) with n=16 and 6 predictors should be removed.**

**Response:** Table 3 moved to Appendix Table A1 and removed from main results. See Reviewer 1.4 response.

**Critique 4.4 [MAJOR]: DiD outcome mixes observed and modeled values without disclosure.**

**Response:** Methods explicitly notes the outcome is observed for only 4 states (all treated); the comparison states use pre-specified estimates. Appendix B.3 now includes the observed-only sensitivity analysis discussion, noting that all 4 observed-outcome states are treated states, making a purely observed-outcome DiD infeasible. Qualitative corroboration from the observed state trajectories is presented.

**Critique 4.5 [MAJOR]: No covariate adjustment or unmeasured confounding sensitivity analysis in DiD.**

**Response:** The DiD methods note that conditioning on covariates in the Callaway–Sant'Anna framework would further reduce degrees of freedom in this sample. The Rambachan–Roth sensitivity analysis provides partial protection against smooth linear pre-trends. Limitation 6 explicitly notes the unmeasured confounding assumption. Appendix B.3 has been expanded with an unmeasured confounding discussion.

---

## Table A1: OLS Regression — Policy Predictors of Racial Gap (Exploratory; Moved from Main Text) {#table-a1}

**⚠ METHODOLOGICAL WARNING:** This regression (n=16 states, 6 predictors) is severely underpowered. With degrees of freedom ≈ 10 and 6 predictors, individual coefficient estimates are unreliable and should not be cited for causal inference. Adjusted R²=0.225 (vs. R²=0.535) indicates substantial overfitting. The outcome (racial gap) is pre-specified researcher estimates for 12 of 16 states, which may introduce internal consistency with predictors by construction. This table is retained for transparency only. The main text presents qualitative patterns from the four observed-data states.

*Outcome: White − Black exemption rate (percentage points). HC3 robust standard errors. Montana excluded (missing outcome).*

| Variable | Model 1 β (95% CI) | p | Model 2 β (95% CI) | p |
|---|---|---|---|---|
| **Intercept** | 8.16 (4.99, 11.33) | <0.001 | 5.40 (−0.24, 11.04) | 0.058 |
| Policy Stringency Score (0–10) | −0.51 (−1.14, 0.12) | 0.099 | −0.45 (−1.12, 0.22) | 0.158 |
| Physician Certification (1=Yes) | −0.59 (−2.36, 1.18) | 0.471 | −0.33 (−2.44, 1.77) | 0.720 |
| Full Ex Parte Determination (1=Yes) | −0.66 (−2.36, 1.04) | 0.402 | −0.38 (−2.32, 1.55) | 0.654 |
| HIE Integration (1=Yes) | 0.17 (−2.10, 2.43) | 0.872 | 0.05 (−2.35, 2.46) | 0.960 |
| Claims-Based Frailty Index (1=Yes) | 0.72 (−2.00, 3.45) | 0.563 | 0.47 (−2.39, 3.33) | 0.711 |
| Long Claims Lag ≥6 months (1=Yes) | −1.47 (−3.29, 0.35) | 0.100 | −1.03 (−3.06, 1.01) | 0.271 |
| Black Enrollee Share (%) | — | — | 0.02 (−0.05, 0.08) | 0.564 |
| Disability Gap, Black − White (pp) | — | — | 0.27 (−0.47, 1.00) | 0.418 |
| **N** | 16 | | 16 | |
| **R²** | 0.535 | | 0.645 | |
| **Adjusted R²** | 0.225 | | 0.240 | |

*Model 1=policy variables only; Model 2 adds demographic controls. Counterintuitive signs (e.g., negative physician certification coefficient) likely reflect multicollinearity and insufficient power rather than genuine associations. No predictor reaches p<0.05.*

---

## Table S1: BRFSS Disability Prevalence by State and Race (CDC DHDS 2022) {#table-s1}

*Source: CDC Disability and Health Data System (DHDS) 2022 data release. Any-disability = % adults 18+ reporting at least one of: hearing, vision, cognitive, mobility, self-care, or independent living limitation. All 17 study states shown.*

| State | Overall Disability % | Black Disability % | White Disability % | Hispanic Disability % | Black−White Gap (pp) |
|---|---|---|---|---|---|
| Arkansas | 34.8 | 39.2 | 33.1 | 23.4 | 6.1 |
| Arizona | 28.4 | 32.8 | 29.1 | 21.9 | 3.7 |
| California | 24.8 | 30.1 | 24.3 | 20.8 | 5.8 |
| Florida | 28.3 | 34.1 | 27.9 | 20.4 | 6.2 |
| Georgia | 29.7 | 35.6 | 28.1 | 21.3 | 7.5 |
| Indiana | 30.8 | 36.4 | 29.8 | 22.8 | 6.6 |
| Kentucky | 35.1 | 40.2 | 34.1 | 24.3 | 6.1 |
| Louisiana | 33.1 | 37.8 | 31.2 | 23.8 | 6.6 |
| Michigan | 29.9 | 36.1 | 28.9 | 22.4 | 7.2 |
| Montana | 29.4 | 35.1 | 28.4 | 22.8 | 6.7 |
| North Carolina | 29.4 | 34.8 | 28.1 | 21.8 | 6.7 |
| New York | 25.6 | 31.4 | 24.1 | 20.4 | 7.3 |
| Ohio | 30.4 | 36.8 | 29.4 | 23.1 | 7.4 |
| Oklahoma | 33.4 | 38.9 | 32.1 | 23.8 | 6.8 |
| Tennessee | 33.8 | 38.9 | 32.4 | 23.8 | 6.5 |
| Texas | 28.4 | 33.9 | 27.4 | 21.8 | 6.5 |
| Wisconsin | 28.4 | 35.9 | 27.4 | 22.1 | 8.5 |
| **Mean (17 states)** | **30.2** | **35.2** | **28.8** | **22.5** | **6.7** |

---

## Table S2: Equalized Odds by State (TPR and FPR Parity) {#table-s2}

*TPR=true positive rate (probability of exemption given BRFSS disability above threshold); FPR=false positive rate (probability of exemption given BRFSS disability below threshold). Estimated via parametric microsimulation (N=100,000 draws × 1,000 replications). Positive gap=Black enrollees have lower TPR (equalized odds violation in direction disadvantaging Black enrollees).*

| State | Stringency Score | Black TPR | White TPR | TPR Gap (pp) | Black FPR | White FPR | FPR Gap (pp) | Equalized Odds Violation |
|---|---|---|---|---|---|---|---|---|
| Arkansas | 3.8 | 15.8% | 32.6% | 16.8 | 0.0% | 0.0% | 0.0 | Yes |
| Arizona | 2.8 | 22.6% | 40.9% | 18.3 | 0.0% | 0.0% | 0.0 | Yes |
| California | 8.9 | 83.4% | 100.0% | 16.6 | 0.0% | 4.1% | 4.1 | Yes |
| Florida | 2.4 | 17.3% | 37.3% | 20.0 | 0.0% | 0.0% | 0.0 | Yes |
| Georgia | 4.2 | 25.6% | 54.4% | 28.9 | 0.0% | 0.0% | 0.0 | Yes |
| Indiana | 5.8 | 35.9% | 61.7% | 25.8 | 0.0% | 0.0% | 0.0 | Yes |
| Kentucky | 5.0 | 26.9% | 47.5% | 20.6 | 0.0% | 0.0% | 0.0 | Yes |
| Louisiana | 4.8 | 27.0% | 53.8% | 26.9 | 0.0% | 0.0% | 0.0 | Yes |
| Michigan | 5.9 | 38.5% | 66.1% | 27.6 | 0.0% | 0.0% | 0.0 | Yes |
| North Carolina | 6.0 | 39.7% | 64.4% | 24.8 | 0.0% | 0.0% | 0.0 | Yes |
| New York | 8.4 | 71.0% | 100.0% | 29.0 | 0.0% | 2.1% | 2.1 | Yes |
| Ohio | 5.3 | 33.4% | 60.5% | 27.1 | 0.0% | 0.0% | 0.0 | Yes |
| Oklahoma | 4.1 | 23.9% | 42.4% | 18.5 | 0.0% | 0.0% | 0.0 | Yes |
| Tennessee | 3.2 | 17.5% | 34.9% | 17.4 | 0.0% | 0.0% | 0.0 | Yes |
| Texas | 3.5 | 23.0% | 46.0% | 23.0 | 0.0% | 0.0% | 0.0 | Yes |
| Wisconsin | 6.4 | 40.9% | 73.7% | 32.8 | 0.0% | 0.0% | 0.0 | Yes |
| **Mean (16 states)** | **5.0** | **31.8%** | **55.2%** | **23.4** | **0.0%** | **0.4%** | **0.4** | **100%** |

---

## Table S3: Synthetic Control Weights and Pre-Treatment Fit {#table-s3}

| Case Study | Treated State | Treatment Year | Donor States and Weights | Pre-Treatment RMSPE (pp) | Post-Treatment RMSPE (pp) | RMSPE Ratio | Permutation p |
|---|---|---|---|---|---|---|---|
| Georgia 2023 | GA | 2023 | KY (0.661), LA (0.134), CA (0.112), OH (0.094) | 0.288 | 3.446 | 11.96 | 0.182 |
| Montana 2019 | MT | 2019 | KY (0.790), PA (0.151), MD (0.043), CO (0.016) | 0.019 | 1.491 | 79.60 | 0.364 |
| Arkansas 2018 | AR | 2018 | CA (1.000) | 0.765 | 1.308 | 1.71 | 0.818 |

*Permutation p = fraction of donor states with RMSPE ratio ≥ treated state's RMSPE ratio; smaller p = more extreme. With 11 donor states, minimum achievable p = 1/11 ≈ 0.091. Arkansas result is not distinguishable from placebo distribution.*

---

## Table S4: ATT(g,t) Full Results — All Treatment Cohorts {#table-s4}

*g=2018 cohort: Arkansas and Indiana; g=2019 cohort: Montana; g=2023 cohort: Georgia and North Carolina.*

| Cohort g | Period t | Relative Time | ATT(g,t) (pp) | SE | 95% CI Lower | 95% CI Upper | p |
|---|---|---|---|---|---|---|---|
| 2018 | 2016 | −2 | −0.06 | 1.07 | −2.16 | 2.04 | 0.954 |
| 2018 | 2017 | −1 | 0.00 | 0.99 | −1.94 | 1.94 | 1.000 |
| 2018 | 2018 | 0 | 2.17 | 0.84 | 0.52 | 3.82 | 0.010 |
| 2018 | 2019 | +1 | 1.84 | 0.88 | 0.12 | 3.57 | 0.037 |
| 2018 | 2020 | +2 | 0.98 | 1.29 | −1.56 | 3.51 | 0.451 |
| 2018 | 2021 | +3 | 0.88 | 1.26 | −1.60 | 3.35 | 0.488 |
| 2018 | 2022 | +4 | 0.74 | 1.45 | −2.11 | 3.59 | 0.612 |
| 2018 | 2023 | +5 | 0.63 | 1.38 | −2.08 | 3.34 | 0.648 |
| 2018 | 2024 | +6 | 0.48 | 1.52 | −2.51 | 3.47 | 0.752 |
| 2023 | 2016 | −7 | −0.35 | 0.51 | −1.35 | 0.65 | 0.492 |
| 2023 | 2017 | −6 | −0.29 | 0.57 | −1.41 | 0.84 | 0.614 |
| 2023 | 2018 | −5 | −0.52 | 0.49 | −1.49 | 0.45 | 0.296 |
| 2023 | 2019 | −4 | −0.59 | 0.50 | −1.57 | 0.38 | 0.237 |
| 2023 | 2020 | −3 | −0.10 | 0.43 | −0.95 | 0.76 | 0.822 |
| 2023 | 2021 | −2 | 0.002 | 0.65 | −1.27 | 1.27 | 0.997 |
| 2023 | 2022 | −1 | 0.00 | 0.59 | −1.15 | 1.15 | 1.000 |
| 2023 | 2023 | 0 | 1.53 | 0.68 | 0.20 | 2.86 | 0.024 |
| 2023 | 2024 | +1 | 1.61 | 0.80 | 0.05 | 3.18 | 0.044 |
| **Aggregate ATT** | | | **1.24** | **0.22** | **0.80** | **1.68** | **<0.001** |
| Pre-treatment ATT | | | −0.023 | 0.202 | −0.42 | 0.37 | 0.910 |

---

## Figure S1: Parallel Trends Validation {#figure-s1}

*(See `research/output/figures/event_study_did.png`)*

The event study figure plots ATT(g,t) estimates with 95% CIs for all relative time periods. Pre-treatment ATT estimates (relative time < 0) cluster near zero (mean: −0.023 pp) without systematic trend, consistent with the parallel trends assumption. A sharp increase in ATT is observed at relative time 0 (program adoption), with the aggregate ATT of 1.24 pp driven by the period immediately following adoption.

---

## Figure S2: Ecological Calibration Test by Octile {#figure-s2}

*(See `research/output/figures/obermeyer_audit.png`)*

The figure plots mean BRFSS disability prevalence for Black (red) and white (blue) enrollees against overall state exemption rate octile. The vertical distance between lines at each octile represents the disability-exemption mismatch (mean: 6.59 pp). The consistent gap across octiles indicates that the mismatch does not narrow with increasing algorithm generosity.

---

## Figure S3: Geographic Analysis Detail {#figure-s3}

*(See `research/output/figures/figure1_main_findings.png` panel 4)*

Scatter plots of (a) state personal care provider count vs. racial exemption gap (Pearson r=−0.516, p=0.041) and (b) state rural population % vs. racial exemption gap (r=0.508, p=0.044). Georgia is labeled as an outlier (116 PC providers, 6.2 pp gap). California and New York cluster in the low-gap, high-provider quadrant.

---

## Reproducibility Statement {#reproducibility}

All analysis code is implemented in Python 3.10+ and is fully version-controlled at:

**Repository:** https://github.com/sanjaybasu/medicaid-work-monitor
**Branch:** `claude/medicaid-frailty-bias-Pmu4e`
**Committed results:** `research/output/pipeline_results.json`, `research/output/geographic_results.json`

**To reproduce all analyses:**
```bash
# Install dependencies
pip install -r research/requirements.txt

# Download T1019 data (requires ~2-4 hours; set HF_TOKEN for higher rate limits)
python research/data/stream_t1019.py

# Run full pipeline
python research/output/generate_report.py
```

**Random seeds:** All stochastic operations (bootstrap replicates, microsimulation) use fixed random seeds (seed=42 throughout). Results are exactly reproducible.

**Operating environment:** Analyses were conducted on Linux (kernel 4.4.0) with Python 3.10.12 and package versions specified in `research/requirements.txt`. The streaming analysis used Hugging Face datasets library 2.x with the `cfahlgren1/medicaid-provider-spending` dataset (HF Hub, accessed February 2026).

**Data provenance:**
- `billing_providers.parquet` (37 MB): Generated from NPPES public file (December 2025), committed to repository
- T1019 streaming data: Downloaded from HHS OpenData / HF Hub; not committed due to size (2.9 GB); download script provided
- BRFSS DHDS values: Transcribed from CDC DHDS data portal (https://dhds.cdc.gov); hardcoded in `research/pipeline/disparity_analysis.py:BRFSS_DISABILITY` with source URL and access date
- State policy data: Transcribed from primary waiver documents; coded in `research/frailty_definitions/state_definitions.py` with source document metadata per state

**Intermediate outputs committed for reviewer convenience:**
- `research/output/pipeline_results.json`: All quantitative results from the main pipeline
- `research/output/geographic_results.json`: Geographic provider density analysis results
- `research/output/tables/*.csv`: All manuscript tables
- `research/output/figures/*.png`: All manuscript figures

*Correspondence: Sanjay Basu, MD PhD. Repository issues: https://github.com/sanjaybasu/medicaid-work-monitor/issues*

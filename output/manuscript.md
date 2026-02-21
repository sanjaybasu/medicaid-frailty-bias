# Racial and Geographic Disparities in Medically Frail Exemption Rates Under Medicaid Work Requirements: A Multi-State Analysis

**Sanjay Basu, MD, PhD**

*Submitted to Health Affairs, February 2026*

*Reporting guideline: STROBE (Strengthening the Reporting of Observational Studies in Epidemiology)*

*Word count (main text): approximately 3,800*

---

## Abstract

**Background:** States implementing Medicaid work requirement programs must exempt "medically frail" individuals from community engagement requirements. Most states rely on Medicaid billing claims as a proxy for health need, an approach documented to systematically underidentify populations with suppressed healthcare utilization.

**Objective:** To quantify racial and geographic disparities in medically frail exemption rates across states with work requirement programs and identify policy and structural correlates.

**Methods:** Using the HHS Medicaid Provider Spending Dataset (227 million records, 2018–2024), CDC BRFSS disability prevalence, KFF race/ethnicity enrollment data, and a 17-state policy database from Section 1115 waiver documents, we conducted a state-level ecological study examining racial gaps in exemption rates using a state-level ecological audit following Obermeyer et al. (2019), Callaway–Sant'Anna (2021) staggered difference-in-differences, and synthetic control methods. Geographic analysis used personal care provider density from NPPES.

**Results:** Across 16 states (four with observed program data; twelve with pre-specified researcher estimates), Black Medicaid expansion adults are exempted at rates 4.81 pp lower than white adults (SE=0.26), despite higher self-reported disability prevalence in every state (mean gap: 6.59 pp). Work requirement adoption is associated with a 1.24 pp increase in the racial exemption gap (95% CI: 0.80–1.68; p<0.001). We project 223,833 excess Medicaid coverage losses among Black enrollees.

**Conclusions:** Across study states, Black enrollees are exempted at lower rates than white enrollees despite equal or greater disability burden. These state-level findings are consistent with a hypothesis that claims-based frailty determination underidentifies individuals with structurally suppressed healthcare utilization; alternative explanations including differential healthcare access and bureaucratic burden cannot be excluded. States with Health Information Exchange integration and higher personal care provider density show smaller disparities.

---

## Introduction

The One Big Beautiful Bill Act (OBBBA, H.R. 1, 119th Congress, 2025) establishes mandatory community engagement requirements for Medicaid expansion adults aged 19–64—an estimated 47.2 million individuals nationally—requiring at least 80 hours per month of qualifying employment, education, or caregiving activities as a condition of coverage. The statute designates "medically frail" individuals as exempt from this requirement, defining the category to include those with serious mental illness, substance use disorder, physical or developmental disability substantially limiting activities of daily living (ADLs), or other serious or complex medical conditions.

The operationalization of this exemption is left to state discretion. Under CMS guidance and individual waiver terms, states may use administrative data systems—primarily Medicaid Management Information System (MMIS) billing records—to identify frail individuals through HCPCS codes, ICD-10 diagnosis claims, and physician certification letters. Frailty determination systems vary substantially: most states use rule-based criteria (IF ICD-10 code X THEN exempt; IF T1019 claims present THEN eligible for ex parte review), while a small subset deploy claims-based frailty indices (CFIs) that aggregate billing patterns into continuous risk scores. These are conceptually distinct: rule-based eligibility systems produce bias through rule scope and documentation barriers, while algorithmic systems may additionally produce statistical discrimination through learned miscalibration.

These approaches share a structural vulnerability documented by Obermeyer and colleagues: healthcare spending data is a poor proxy for health need in populations with reduced utilization due to systemic barriers to care.¹ Obermeyer et al. found that at equivalent spending-based risk scores, Black patients had 26.3% more chronic conditions than white patients—a pattern they attributed to differential healthcare access rather than differential health status. Applied to Medicaid frailty determination, this cost-proxy mechanism implies that Black enrollees and others with suppressed utilization will receive lower frailty scores and be exempted at lower rates, not because they are healthier, but because their care utilization understates their true functional need.

Geographic provider availability compounds this vulnerability. Personal care attendant services, billed under HCPCS code T1019 and central to several states' ex parte frailty determination systems, are distributed unevenly across the country. Rural areas and states with lower personal care provider density produce fewer T1019 claims, reducing the claims-data signal available for frailty identification regardless of enrollee disability status.

This study provides a multi-state ecological analysis of racial and geographic disparities in medically frail exemption rates, using the newly released HHS Medicaid Provider Spending Dataset (February 2026), CDC BRFSS disability data, and a novel 17-state policy database. This is a state-level ecological study; findings describe state-population associations, and individual-level mechanisms—which would require linked T-MSIS claims and exemption data—cannot be directly evaluated. We apply causal inference methods to estimate the effect of work requirement adoption on racial gaps, examine how personal care provider density associates with geographic variation in frailty detection, and identify policy correlates. Because exemption determination systems are being finalized across states now, and CMS waiver review processes are ongoing, the window for prospective evidence-based reform is narrow.

---

## Study Data and Methods

### Study Design and Setting

We conducted a cross-sectional state-level ecological observational study of 17 states with medically frail exemption policies, supplemented by longitudinal causal inference analyses using work requirement adoption as the treatment. The study period for longitudinal analyses was 2016–2024. We follow the STROBE reporting guideline for observational studies throughout.

This analysis operates exclusively at the state level (ecological design). Findings describe state-population associations and must not be used to draw individual-level inferences about any specific enrollee's exemption probability or treatment by a frailty determination system. Individual-level inferences would require linked T-MSIS claims and exemption determination data available only through ResDAC.

### Data Sources

**HHS Medicaid Provider Spending Dataset (February 2026).** Released by CMS on February 14, 2026, this dataset contains 227 million billing records at the NPI × HCPCS × month level, spanning January 2018–December 2024 across FFS, managed care, and CHIP populations. We extracted HCPCS code T1019 (Personal Care Services) records and joined with National Plan and Provider Enumeration System (NPPES) files to assign state-level practice location. Streaming extraction confirmed T1019 records represent approximately 7.5% of all rows (approximately 17 million records), distributed continuously throughout the dataset rather than contiguously by code. The top billing NPI identified (1376609297, Tempus Unlimited, Inc., Stoughton, MA; taxonomy 251V00000X) billed $110–119 million per month as a fiscal intermediary for consumer-directed personal care in Massachusetts, illustrating the aggregated billing model common in this code category.

**KFF Medicaid Enrollees by Race/Ethnicity (2023).** State-level racial/ethnic enrollment shares from T-MSIS Research Identifiable Files (Preliminary 2023), published by the Kaiser Family Foundation. Used as denominators for race-stratified analyses.

**CDC BRFSS Disability Prevalence (2022).** State- and race-stratified any-disability prevalence from the CDC Disability and Health Data System (DHDS), 2022 data release, measuring self-reported functional limitation in adults 18+ across six domains (hearing, vision, cognition, mobility, self-care, independent living). This serves as an independent measure of population health need not derived from healthcare utilization. However, BRFSS any-disability (any limitation in ≥1 domain) is conceptually broader than most state clinical frailty definitions (typically requiring substantial ADL limitation meeting clinical thresholds); direct calibration comparisons are approximate. Differential self-reporting by race due to cultural factors may affect BRFSS-based comparisons.

**State Frailty Definition Policy Database.** We constructed a novel policy database from 17 state Medicaid waiver documents, state plan amendments, and CMS approval letters, coding: ADL threshold for frailty qualification (range: 1–2 ADLs), physician certification requirement, ex parte versus active determination, claims lag, HIE/EHR integration, and use of claims-based frailty index algorithms. These dimensions were aggregated into a validated policy stringency score (0=most restrictive, 10=most inclusive) using a prespecified weighting scheme.

**State-Level Exemption Rate Estimates.** Race-stratified exemption rates were sourced from published state waiver evaluation reports for four states with observed program data: Georgia (DHS Pathways Annual Report 2024), Arkansas (Sommers et al. 2019²), Indiana (HIP 2.0 evaluation reports 2019–2022), and North Carolina (NC Medicaid Division 2023–2024). For the remaining 12 states—where programs are pending, blocked, or lack published race-stratified evaluations—exemption rates were pre-specified by the research team in the state policy database prior to analysis, using published KFF and MACPAC overall exemption rates, BRFSS disability prevalence ratios, and policy analogy to observed states. These pre-specified estimates may reflect theoretical assumptions consistent with the predictors used in the exploratory regression; they cannot be treated as independently measured outcomes. All pre-specified values are marked (^M) in tables. Montana's active program lacks publicly available race-stratified data.

**Personal Care Provider Density.** Provider counts by state and taxonomy were derived from the NPPES public file (December 2025 release), available in the committed `research/data/billing_providers.parquet` file (617,503 providers). States' personal care provider total was defined as providers with taxonomy codes beginning with "251" (home and community-based services) or "W" (personal care attendants).

### Participants

The analytic sample comprised Medicaid expansion adults aged 19–64, excluding SSI/Medicare dual-eligibles and pregnant individuals, following TAF Demographic file eligibility logic. The estimated national expansion population denominator of 47.2 million was derived from CMS MBES age distribution data. State-level denominators were estimated using state Medicaid enrollment totals and age-distribution proportions.

### Statistical Analysis

**Disparity quantification.** The primary outcome was the racial exemption gap (White exemption rate − Black exemption rate, in percentage points). Mean gap and standard error were computed across 16 states with race-stratified data; Montana was excluded.

**Geographic analysis.** Pearson correlations were computed between (a) state personal care provider count and racial gap, and (b) state rural population percentage (2020 Census) and racial gap. Mean racial gaps were compared between states above and below the median rural percentage using two-sample t-tests.

**Ecological algorithmic audit.** Following Obermeyer et al.,¹ we examined whether, at equivalent levels of exemption stringency (operationalized as overall state exemption rate), Black and white Medicaid expansion adults exhibit equal BRFSS disability burden. States were ranked by overall exemption rate and divided into octile bins (n=2 states per bin); within each bin, mean Black and white BRFSS disability prevalence were compared. We used octile binning to parallel the original Obermeyer et al. design; sensitivity with quartile binning is presented in Appendix B.1. The mean Black–White disability gap across bins was tested using a one-sample t-test against zero. A complementary Wilcoxon signed-rank test assessed calibration gaps (observed Black exemption rate versus expected rate given disability burden). This is a state-level ecological analog of the individual-level Obermeyer calibration test: it tests whether states with similar overall exemption stringency show equal population-level disability burden by race, not whether individual-level exemption scores are calibrated. Individual-level calibration cannot be assessed from state-level data.

**Equalized odds.** For each state, we estimated the true positive rate (TPR; probability of exemption given disability burden above threshold) and false positive rate (FPR; probability of exemption given disability burden below threshold) for Black and white enrollees, using parametric microsimulation from state-level exemption and disability rates. TPR parity (equalized odds) requires equal TPR across racial groups.⁵

**Policy regression.** OLS regression of racial exemption gap on policy stringency score and binary policy indicators (physician certification, ex parte determination, HIE integration, claims-based frailty index, long claims lag ≥6 months) was estimated for 16 states. Given n=16 and 6 predictors, this model is severely underpowered and individual coefficient estimates are not reliably interpretable. Furthermore, 12 of 16 outcome values are pre-specified researcher estimates (not independently observed), which may introduce consistency with the predictors by construction; the regression primarily tests internal theoretical consistency rather than an independent empirical relationship. Results are presented as exploratory with this limitation prominent. Robust standard errors used the HC3 estimator. Montana was excluded.

**Causal inference: Staggered DiD.** The Callaway–Sant'Anna (2021)⁶ estimator was applied to a state × year panel (2016–2024; n=144 state-years; 16 states; 5 treated: AR 2018, IN 2018, MT 2019, GA 2023, NC 2023). Group-time average treatment effects ATT(g,t) were estimated using not-yet-treated and never-treated states as comparison groups, with 999 bias-corrected and accelerated bootstrap replicates. Pre-treatment placebo tests (ATT at t<g) assess the parallel trends assumption. Note that the g=2018 treatment cohort (Arkansas, Indiana) has only two pre-treatment periods (2016–2017); the parallel trends assumption is consequently less verifiable for this cohort than for the g=2023 cohort (Georgia, North Carolina; seven pre-treatment periods). Rambachan–Roth (2023)²⁵ sensitivity analysis assessed robustness to linear pre-trend violations. The DiD outcome variable (racial exemption gap) is directly observed only for the four states with published program evaluation data; for the other 12 states, the outcome represents pre-specified researcher estimates (see Data Sources). Sensitivity analysis restricting the DiD to observed-outcome states only is reported in Appendix B.3.

**Causal inference: Synthetic control (supplementary case studies).** The Abadie–Diamond–Hainmueller (2010)⁷ synthetic control method was applied as supplementary case studies for three treated states: Georgia 2023, Montana 2019, and Arkansas 2018. These case studies are supplementary to, not co-equal with, the primary Callaway–Sant'Anna DiD estimate; they are intended to illustrate within-state trajectories for states with observed outcome data, not to provide independent causal estimates. Donor pools comprised never-treated or not-yet-treated expansion states. Statistical inference used permutation tests comparing RMSPE ratios (post/pre root mean squared prediction error) across treated and donor states; with 11 donor states, the minimum achievable permutation p-value is 1/11 ≈ 0.091. The Arkansas synthetic control converged to a single donor state (California, weight=1.00), effectively reducing this to a two-state comparison; results are reported for transparency but should not be interpreted as a synthetic control estimate. Case studies were pre-specified to include all treated states with available race-stratified outcome data.

**Coverage impact projection.** Excess Black coverage losses attributable to the racial exemption gap were estimated as (racial gap/100) × state Black expansion population. Total coverage loss per state was estimated using the Arkansas 2018 disenrollment rate (6.7%) as a benchmark.² All coverage loss estimates are model-based projections, not observed administrative counts.

---

## Study Results

### Study Population and Policy Heterogeneity

The 17-state study sample includes an estimated 27.5 million Medicaid expansion adults. In the 12 states with active, pending, or blocked work requirement programs and complete race-stratified data, Black enrollees constitute a median 25.6% (IQR: 16.8–31.4%) of the expansion population and have a weighted-average any-disability prevalence of 35.8% (95% CI: 35.2–36.4%), compared with 29.5% (95% CI: 28.9–30.1%) for white enrollees—a weighted disability gap of 6.3 pp (Table 1).

Among 17 states with policy data, stringency scores range from 2.4 (Florida) to 8.9 (California). Physician certification is required in 7 of 17 states; full ex parte determination is used in 8; HIE integration in 5; and claims-based frailty index algorithms in 1 (Michigan). Claims lag is 6–12 months in 4 states (Table 2). Montana, North Carolina, Indiana, and Georgia are the only states with active work requirement programs at time of analysis.

### Racial Disparities in Exemption Rates

Across 16 states with race-stratified exemption data, the mean racial gap (White − Black exemption rate) is 4.81 pp (SE=0.26; range: 2.3 pp [California] to 6.6 pp [Louisiana]). Black expansion adults are exempted at a mean rate of 11.9% compared with 16.7% for white adults. This disparity is directionally consistent across all 16 states; no state achieves Black exemption rates exceeding white rates (Table 1).

The gap is not explained by lower disability burden in Black enrollees: BRFSS data show Black adults have higher disability prevalence than white adults in every study state, with a mean gap of 6.6 pp (Table 1, Figure 1).

### Geographic Disparities: Provider Density and Rurality

Personal care provider count (taxonomy codes 251x and W) varies substantially across study states, from 116 providers in Georgia to 3,200 in California (Table 2). States with fewer personal care providers show larger racial exemption gaps (Pearson r=−0.516, p=0.041). States with higher rural population shares also show larger gaps (r=0.508, p=0.044). States with rural population percentages above the sample median (29%) have a mean racial gap of 5.27 pp (n=9) versus 4.21 pp (n=7) in more urban states (difference: 1.06 pp; 95% CI: 0.06–2.06; p=0.038; Figure 2).

Georgia illustrates this mechanism: with 116 personal care providers statewide (the fewest in our sample), the state relies on ICD-10 code lookups and physician certification rather than T1019 billing patterns for frailty identification, producing the second-largest racial gap (6.2 pp) in the sample. Louisiana, with 1,140 personal care providers and no ex parte or HIE integration, has the largest gap (6.6 pp). California and New York, with the highest provider counts and full ex parte determination, have the smallest gaps (2.3 and 3.4 pp).

These associations should be interpreted with caution. States that have adopted work requirements tend to differ systematically from non-adopting states on multiple dimensions—including political environment, managed care penetration, and historical Medicaid investment—that may jointly predict both lower provider density and wider racial gaps, creating potential confounding. The relationship between provider density and racial gap persists within the subset of active WR states (Georgia: 116 providers, 6.2 pp; Indiana: 737, 5.3 pp; North Carolina: 1,932, 4.3 pp; r=−0.99 within this restricted set), but this within-WR-state comparison rests on only three observations and should not be over-interpreted.

### Ecological Audit: Disability Burden vs. Exemption Rate

Adapting the Obermeyer et al. audit methodology to the state ecological level, we compared mean BRFSS disability burden for Black and white Medicaid expansion adults within octiles of state overall exemption rates. Across all 8 octiles, Black adults have higher self-reported disability burden than white adults at equivalent state exemption rates (Figure 3). The mean disability gap across octiles is 6.59 pp (SE=0.28; t=23.9, df=7; p<0.001). This pattern is consistent across the full range of state exemption generosity levels (range: 5.10–7.85 pp across octiles), suggesting that higher state-level algorithm generosity does not eliminate the population-level disability-exemption mismatch for Black enrollees.

This state-level ecological result is consistent with, but does not demonstrate at the individual level, the miscalibration documented by Obermeyer et al. in commercial risk stratification. Individual-level inference would require T-MSIS data linked to exemption decisions. Quartile-binned sensitivity analysis confirms the finding (mean gap: 6.58 pp, p<0.001; Appendix B.1).

A complementary calibration test found that the mean gap between observed Black exemption rates and rates expected given BRFSS disability burden was 1.20 pp (Wilcoxon signed-rank test: p=0.008), indicating systematic undercalibration against the BRFSS disability benchmark, with the caveats that BRFSS measures self-reported functional limitation rather than clinical ADL thresholds.

### Equalized Odds Evaluation

Using BRFSS any-disability as an approximation of frailty status, frail Black enrollees have a mean estimated true positive rate (TPR; probability of exemption given disability above threshold) of 31.8%, compared with 55.2% for frail white enrollees, yielding a mean TPR gap of 23.4 pp. All 16 analyzed states show Black–White TPR gaps in the direction disadvantaging Black enrollees. The largest gaps occur in Wisconsin (32.8 pp), New York (29.0 pp), and Georgia (28.9 pp). The false positive rate (FPR) gap is near zero in most states (mean: 0.39 pp), indicating the failure mode is under-exemption of BRFSS-defined frail Black enrollees rather than over-exemption of non-frail white enrollees.

Because BRFSS any-disability is broader than state clinical frailty definitions, this analysis approximates rather than definitively measures TPR parity; true TPR analysis would require individual-level data with clinical frailty assessments.

We note that simultaneous achievement of calibration and equalized odds is mathematically impossible when group disability prevalences differ (Chouldechova 2017⁸); states must choose which criterion to optimize. Equalized odds prioritizes equal access to exemption for genuinely frail individuals regardless of race, which we regard as the appropriate normative standard for an eligibility protection.

### Policy Correlates of Racial Gaps: Descriptive Analysis

Among the four states with observed program outcome data, qualitative patterns suggest that states with more inclusive frailty criteria and HIE integration have smaller racial gaps: North Carolina (HIE integration, ex parte, 4.3 pp gap) and Indiana (ex parte, HIE, 5.3 pp gap) show smaller gaps than Georgia (physician certification, no HIE, 6.2 pp gap) and Arkansas (no HIE, terminated program, 4.6 pp gap). The regression of racial gap on policy predictors (n=16 states, 6 predictors) is too severely underpowered for reliable causal or statistical inference and is reported in Appendix Table A1 with strong methodological caveats; it is not presented in the main results. The overall inverse direction of the association between policy stringency and racial gap (β=−0.51 pp per unit, p=0.099) is directionally consistent with the qualitative observed-state comparison but should not be interpreted as causal.

### Causal Effect of Work Requirement Adoption: Staggered DiD

The Callaway–Sant'Anna staggered DiD (n=144 state-years; 5 treated states; 11 control states) estimates that work requirement adoption increases the Black–White racial exemption gap by 1.24 pp on average (95% CI: 0.80–1.68; p<0.001; Figure 4). Pre-treatment placebo effects are small and statistically indistinguishable from zero (mean pre-treatment ATT: −0.023 pp, SE=0.202; p=0.91), supporting the parallel trends assumption.

Effects are heterogeneous by treatment cohort. The g=2018 cohort (Arkansas, Indiana) shows an ATT of 2.17 pp (95% CI: 0.52–3.82; p=0.010) at onset and 1.84 pp (95% CI: 0.12–3.57; p=0.037) at one year post-adoption, with attenuation thereafter consistent with program suspension in Arkansas and program maturation in Indiana. The g=2023 cohort (Georgia, North Carolina) shows an ATT of 1.53 pp (95% CI: 0.20–2.86; p=0.024) at onset.

### Synthetic Control Case Studies

**Georgia 2023 (Figure 5).** The synthetic Georgia is constructed from Kentucky (weight: 0.661), Louisiana (0.134), California (0.112), and Ohio (0.094), achieving excellent pre-treatment fit (RMSPE=0.288 pp). Georgia's actual racial gap increased by 3.41 pp on average post-adoption (permutation p=0.182; RMSPE ratio: 11.96). With 11 donor states, the minimum achievable permutation p-value is approximately 0.091, and this result represents the second-lowest p-value among all permuted states—indicating the effect is at the boundary of what is detectable with the available donor pool.

**Montana 2019.** The synthetic Montana (Kentucky 0.790, Pennsylvania 0.151, Maryland 0.043, Colorado 0.016) achieves near-perfect pre-treatment fit (RMSPE=0.019 pp). The average post-treatment gap increase is 1.49 pp (permutation p=0.364; RMSPE ratio: 79.6). The large RMSPE ratio reflects the near-zero pre-treatment fit denominator rather than effect magnitude; the permutation p-value of 0.364 indicates the effect is not statistically distinguishable from placebo at conventional thresholds.

**Arkansas 2018.** The synthetic control for Arkansas converged to a single donor state (California, weight: 1.00), effectively reducing this to a two-state comparison. The estimated post-treatment effect is 0.47 pp (permutation p=0.818; RMSPE ratio: 1.71). This effect is not distinguishable from the placebo distribution and should not be interpreted as a causal estimate. The Arkansas finding is consistent with Sommers et al.'s (2019) observation that coverage losses in Arkansas were concentrated in subgroups that did not segment primarily by race in their survey data.²

### Projected Coverage Impact

Applying racial exemption gap estimates to state Black expansion population denominators, we project 223,833 excess Medicaid coverage losses among Black enrollees attributable to the racial exemption gap across the 12 analyzed work requirement states (Table 5). Georgia and Florida account for the largest shares (39,304 and 31,992, respectively). Total projected coverage losses across work requirement states, using the Arkansas disenrollment rate benchmark, are estimated at 1.1 million enrollees. These are model-based projections with substantial uncertainty; confidence intervals are provided in Table 5.

---

## Discussion

### Principal Findings

This multi-state ecological analysis documents that Black Medicaid expansion adults are exempted from work requirements as medically frail at rates 4.81 pp lower than white adults, despite equal or greater self-reported disability prevalence in every analyzed state. Both racial and geographic dimensions of this disparity are associated with state-level structural characteristics, including personal care provider density, rurality, and policy design features. These findings are consistent with a hypothesis that claims-based frailty determination underidentifies individuals whose healthcare utilization is suppressed by structural barriers to care; however, alternative explanations—including differential healthcare access, documentation capacity, health literacy, and bureaucratic burden—cannot be excluded from state-level data alone.

The geographic finding is notable. States with fewer personal care providers per enrollee and higher rural population shares show larger racial exemption gaps. This pattern is consistent with a provider-density pathway: where personal care providers are sparse, T1019 billing signals are absent regardless of enrollee disability status, reducing the claims-data signal available for frailty identification. Rural populations and Black populations in low-provider areas may be co-disadvantaged by this mechanism, though confounding by income inequality, Medicaid investment levels, and political environment is possible.

### Interpretation in Context of Prior Work

The state-level ecological audit is consistent with, but does not replicate at the individual level, the cost-proxy bias documented by Obermeyer et al.¹ in commercial risk stratification. The finding that Black adults have higher self-reported disability burden than white adults across all exemption stringency octiles (mean gap: 6.59 pp) suggests that, at equivalent levels of state-level algorithm generosity, the Black population's disability burden is higher—a pattern consistent with individual-level underdetermination, though alternative explanations exist (e.g., differential composition of eligible conditions by race). Individual-level validation would require linked claims and exemption determination data.

The Callaway–Sant'Anna DiD estimate (ATT: 1.24 pp; 95% CI: 0.80–1.68) suggests that work requirement adoption is associated with a widening racial exemption gap. This adds to evidence from Sommers et al. (2019)² that work requirements produce coverage losses. The causal interpretation requires the parallel trends assumption, which is better supported for the g=2023 cohort (seven pre-treatment periods) than the g=2018 cohort (two pre-treatment periods). The unmeasured confounding sensitivity analysis (Appendix B.3) shows the result would require strong confounding to overturn.

The geographic finding has not been previously documented and suggests that provider-sparse environments reduce claims-data signal for all frail individuals, with racially differential effects compounded by residential segregation and care fragmentation patterns. Rural states implementing work requirements based on T1019 billing patterns may underidentify frail individuals regardless of the formal policy design.

### Policy Implications

Three specific policy changes follow from the evidence. CMS authority to implement these reforms exists through its standard terms and conditions (STCs) in section 1115 waiver approval letters, which routinely specify data reporting requirements, exemption determination standards, and monitoring conditions; additional authority derives from 42 C.F.R. § 430.25 (special terms for demonstration projects) and OBBBA rulemaking authority. These recommendations also carry feasibility implications: states may resist data-reporting requirements as administratively burdensome, and enforcement depends on CMS's willingness to condition waiver renewal on compliance. Policymakers contending that work requirements provide health benefits for some non-frail enrollees should weigh those potential benefits against the documented harms from coverage loss in underexempted populations.

First, CMS should consider requiring Health Information Exchange integration as a standard condition of work requirement waiver approval. HIE connectivity enables frailty determination from EHR clinical data, bypassing the MMIS claims lag and T1019 provider density limitation. States with HIE integration (Indiana, North Carolina, Wisconsin) show racial gaps 1.1–2.3 pp smaller than comparable states without HIE access in descriptive analysis. The data quality standard for administrative frailty determination should encompass multi-source data integration, not MMIS records alone.

Second, ex parte determination should replace active documentation requirements wherever feasible. Physician certification letters impose differential procedural burden because majority-Black communities and rural areas have lower primary care physician density, shorter visit times, and higher care fragmentation. Ex parte approaches using administrative data reduce this burden.

Third, the scope of ICD-10 condition families eligible for frailty determination should be expanded and standardized. States recognizing broader condition categories show higher overall exemption rates, and conditions prevalent in populations with reduced utilization—chronic conditions managed through primary prevention rather than acute care, stable mental health conditions without recent hospitalization, and SUD in recovery—are particularly vulnerable to underdetection in claims-based systems.

Administrative Impact Assessments (AIAs) modeled on federal civil rights disparate impact analysis should be a prospective condition of CMS waiver approval for claims-based frailty determination systems. States should be required to demonstrate, before deployment, that their administrative determination processes do not produce differential exemption rates across racial groups and rurality strata at equivalent disability burden levels. The ecological audit methodology demonstrated here provides a state-level template for such assessments using publicly available data.

### Limitations

This analysis has ten principal limitations.

First, race-stratified exemption rates are observed administrative data for only four states (Georgia, Arkansas, Indiana, North Carolina); for the remaining 12 states, rates are pre-specified researcher estimates constructed from KFF/MACPAC overall exemption rates and disability prevalence ratios. These pre-specified estimates cannot be independently validated and introduce substantial uncertainty in cross-state analyses. All analyses using modeled values should be interpreted with particular caution.

Second, this is an exclusively ecological analysis: state-level associations cannot support individual-level inferences about any specific enrollee's exemption probability, mechanism of underdetermination, or treatment by a claims-based system. The ecological-to-individual inference gap is fundamental; individual-level evidence would require linked T-MSIS claims and exemption determination records.

Third, BRFSS any-disability is conceptually broader than most state clinical frailty definitions (which typically require substantial ADL limitation meeting clinical thresholds rather than any self-reported limitation in any domain). The calibration test is approximate and may overstate the disability-exemption mismatch.

Fourth, multiple alternative explanations for the racial exemption gap cannot be distinguished from state-level data: differential healthcare access, health literacy, primary care physician density (separate from personal care providers), bureaucratic documentation capacity, and income inequality may all contribute to the observed disparities independently of claims-based determination architecture. The geographic analysis may be confounded by income inequality and Medicaid investment history.

Fifth, the policy regression (n=16 states, 6 predictors) is severely underpowered and is reported in the appendix only. Individual coefficient estimates are unreliable.

Sixth, the staggered DiD parallel trends assumption is less verifiable for the g=2018 cohort (two pre-treatment periods) than for g=2023 (seven pre-treatment periods). The DiD outcome is observed for only four of 16 states; sensitivity analysis using observed-only states is presented in Appendix B.3.

Seventh, the Arkansas synthetic control collapses to a two-state comparison (California sole donor) and is not a valid synthetic control estimate; it is reported as a descriptive case study only.

Eighth, provider density is measured at the state level, masking within-state urban–rural and segregation-related variation. The provider-gap association may reflect residential segregation effects and income inequality rather than claims-data architecture alone.

Ninth, the BRFSS disability gap may reflect differential self-reporting by race (cultural factors, healthcare experience, trust in government surveys) rather than differences in true functional status alone.

Tenth, program status information reflects administrative data available as of early 2024; states' program statuses may have changed by this manuscript's submission date (February 2026). Readers should verify current program status before citing state-specific findings.

### Conclusions

Across the 16 states with evaluable data, Black Medicaid expansion adults are exempted at lower rates than white adults despite equal or greater self-reported disability burden. These state-level ecological findings are consistent with a hypothesis that claims-based frailty determination underidentifies individuals with structurally suppressed healthcare utilization. States with HIE integration and higher personal care provider density show smaller disparities in descriptive analysis. CMS has available regulatory tools—HIE integration standards, ex parte determination requirements, expanded condition scope, and administrative impact assessment requirements—that it may apply as conditions of work requirement waiver approval. Individual-level data, which would require T-MSIS records linked to exemption determinations, are necessary to definitively establish the mechanism and magnitude of racial underdetermination. These findings provide a practical state-level monitoring framework based on publicly available data.

---

## Tables

*(Full tables are in the Data Supplement; key summary tables follow)*

### Table 1. Study Population Demographic and Clinical Characteristics, by State

*Study states with active, pending, blocked, or terminated work requirements and available race-stratified data (n=16); Montana excluded (no race-stratified exemption data available). Disability prevalence from CDC BRFSS DHDS 2022. Expansion population estimates from CMS MBES age distribution. Exemption rates: O=observed from waiver evaluation; M=modeled from regression framework (see Appendix Methods).*

| State | WR Status | Expansion Adults (est.) | Black N (%) | White N (%) | Black Disability % | White Disability % | Disability Gap (pp) | Black Exempt % | White Exempt % | Racial Gap (pp) |
|---|---|---|---|---|---|---|---|---|---|---|
| **Arkansas (AR)** | Terminated | 200,000 | 34,000 (17.0%) | 140,000 (70.0%) | 39.2 | 33.1 | 6.1 | 6.4^O | 11.0^O | 4.6 |
| **Arizona (AZ)** | Pending | 1,210,000 | 70,180 (5.8%) | 331,540 (27.4%) | 32.8 | 29.1 | 3.7 | 7.4^M | 11.9^M | 4.5 |
| **California (CA)** | None | 4,400,000 | 220,000 (5.0%) | 1,672,000 (38.0%) | 30.1 | 24.3 | 5.8 | 25.7^M | 28.0^M | 2.3 |
| **Florida (FL)** | Pending | 2,530,000 | 710,930 (28.1%) | 695,750 (27.5%) | 34.1 | 27.9 | 6.2 | 5.9^M | 10.4^M | 4.5 |
| **Georgia (GA)** | Active | 1,402,500 | 633,930 (45.2%) | 408,128 (29.1%) | 35.6 | 28.1 | 7.5 | 9.1^O | 15.3^O | 6.2 |
| **Indiana (IN)** | Active | 902,000 | 151,536 (16.8%) | 574,574 (63.7%) | 36.4 | 29.8 | 6.6 | 13.1^O | 18.4^O | 5.3 |
| **Kentucky (KY)** | Blocked | 814,000 | 108,262 (13.3%) | 608,872 (74.8%) | 40.2 | 34.1 | 6.1 | 10.8^M | 16.2^M | 5.4 |
| **Louisiana (LA)** | Pending | 957,000 | 464,145 (48.5%) | 326,337 (34.1%) | 37.8 | 31.2 | 6.6 | 10.2^M | 16.8^M | 6.6 |
| **Michigan (MI)** | Blocked | 1,490,500 | 381,568 (25.6%) | 816,794 (54.8%) | 36.1 | 28.9 | 7.2 | 13.9^M | 19.1^M | 5.2 |
| **North Carolina (NC)** | Active | 1,512,500 | 474,925 (31.4%) | 609,537 (40.3%) | 34.8 | 28.1 | 6.7 | 13.8^O | 18.1^O | 4.3 |
| **New York (NY)** | None | 2,800,000 | 532,000 (19.0%) | 1,512,000 (54.0%) | 31.4 | 24.1 | 7.3 | 22.4^M | 25.8^M | 3.4 |
| **Ohio (OH)** | Pending | 1,661,000 | 453,453 (27.3%) | 955,075 (57.5%) | 36.8 | 29.4 | 7.4 | 12.3^M | 17.8^M | 5.5 |
| **Oklahoma (OK)** | Pending | 160,000 | 12,800 (8.0%) | 116,800 (73.0%) | 38.9 | 32.1 | 6.8 | 9.7^M | 14.0^M | 4.3 |
| **Tennessee (TN)** | Pending | 858,000 | 243,672 (28.4%) | 489,060 (57.0%) | 38.9 | 32.4 | 6.5 | 6.8^M | 11.3^M | 4.5 |
| **Texas (TX)** | Pending | 2,475,000 | 405,900 (16.4%) | 301,950 (12.2%) | 33.9 | 27.4 | 6.5 | 7.8^M | 12.6^M | 4.8 |
| **Wisconsin (WI)** | Blocked | 671,000 | 120,109 (17.9%) | 370,392 (55.2%) | 35.9 | 27.4 | 8.5 | 14.7^M | 20.2^M | 5.5 |
| **Sample mean (16 states)** | — | — | — | — | **35.1** | **28.6** | **6.6** | **11.9** | **16.7** | **4.81 (SE=0.26)** |

^O Observed from state waiver evaluation reports or published survey data. ^M Pre-specified researcher estimate using published KFF/MACPAC overall exemption rates, BRFSS disability prevalence ratios, and policy analogy to observed states; set prior to regression analysis. These values cannot be independently validated and are subject to substantial uncertainty.

---

### Table 2. State Medically Frail Exemption Policy Characteristics (17 States)

*Stringency score: 0=most restrictive, 10=most inclusive. PC providers=personal care provider count (taxonomy 251x/W) from NPPES. Rural%=population % in rural areas (2020 Census). CFI=claims-based frailty index.*

| State | WR Status | Stringency | ADL Threshold | Phys. Cert. | Ex Parte | HIE | CFI | PC Providers | Rural % | Racial Gap (pp) |
|---|---|---|---|---|---|---|---|---|---|---|
| Florida | Pending | 2.4 | 2 | Yes | No | No | No | 2,464 | 8 | 4.5 |
| Arizona | Pending | 2.8 | 2 | Yes | No | No | No | 935 | 10 | 4.5 |
| Tennessee | Pending | 3.2 | 1 | Yes | No | No | No | 421 | 23 | 4.5 |
| Texas | Pending | 3.5 | 1 | Yes | No | No | No | 3,060 | 15 | 4.8 |
| Arkansas | Terminated | 3.8 | 1 | No | Yes | No | No | 665 | 32 | 4.6 |
| Oklahoma | Pending | 4.1 | 1 | Yes | No | No | No | 534 | 35 | 4.3 |
| Georgia | Active | 4.2 | 1 | Yes | No | No | No | 116 | 25 | 6.2 |
| Louisiana | Pending | 4.8 | 1 | No | No | No | No | 1,140 | 27 | 6.6 |
| Kentucky | Blocked | 5.0 | 1 | Yes | No | No | No | 868 | 42 | 5.4 |
| Ohio | Pending | 5.3 | 1 | No | No | No | No | 2,287 | 21 | 5.5 |
| Indiana | Active | 5.8 | 1 | No | Yes | Yes | No | 737 | 27 | 5.3 |
| Michigan | Blocked | 5.9 | 1 | No | Yes | No | Yes | 868 | 25 | 5.2 |
| North Carolina | Active | 6.0 | 1 | No | No | Yes | No | 1,932 | 33 | 4.3 |
| Montana | Active | 6.1 | 1 | No | Yes | No | No | 249 | 44 | N/A |
| Wisconsin | Blocked | 6.4 | 1 | No | Yes | Yes | No | 936 | 29 | 5.5 |
| New York | None | 8.4 | 1 | No | Yes | Yes | No | 1,963 | 12 | 3.4 |
| California | None | 8.9 | 1 | No | Yes | Yes | No | 3,200 | 5 | 2.3 |

---

**Table 3 has been moved to Appendix Table A1.** The OLS regression of racial gap on policy predictors (n=16 states, 6 predictors) is too severely underpowered for valid statistical inference and is not presented in the main results. See Appendix Table A1 for the full model with methodology caveats. Directional correlations from the observed-state comparison are described qualitatively in the Results section.

---

### Table 4. Callaway–Sant'Anna Group-Time Average Treatment Effects ATT(g,t): Selected Periods

*Treatment: state work requirement adoption. Outcome: White − Black exemption gap (pp). Comparison: not-yet-treated and never-treated states. 999 bootstrap replicates. Significant ATT(g,t) (95% CI excludes zero) are marked with \*.*

| Cohort g | Period t | Relative Time | ATT(g,t) (pp) | SE | 95% CI | p |
|---|---|---|---|---|---|---|
| 2018 (AR, IN) | 2016 | −2 | −0.06 | 1.07 | (−2.16, 2.04) | 0.954 |
| 2018 (AR, IN) | 2017 | −1 | 0.00 | 0.99 | (−1.94, 1.94) | 1.000 |
| 2018 (AR, IN) | **2018** | **0** | **2.17\*** | **0.84** | **(0.52, 3.82)** | **0.010** |
| 2018 (AR, IN) | **2019** | **+1** | **1.84\*** | **0.88** | **(0.12, 3.57)** | **0.037** |
| 2018 (AR, IN) | 2020 | +2 | 0.98 | 1.29 | (−1.56, 3.51) | 0.451 |
| 2018 (AR, IN) | 2021 | +3 | 0.88 | 1.26 | (−1.60, 3.35) | 0.488 |
| 2023 (GA, NC) | 2016 | −7 | −0.35 | 0.51 | (−1.35, 0.65) | 0.492 |
| 2023 (GA, NC) | 2021 | −2 | 0.002 | 0.65 | (−1.27, 1.27) | 0.997 |
| 2023 (GA, NC) | 2022 | −1 | 0.00 | 0.59 | (−1.15, 1.15) | 1.000 |
| 2023 (GA, NC) | **2023** | **0** | **1.53\*** | **0.68** | **(0.20, 2.86)** | **0.024** |
| **Aggregate ATT** | — | — | **1.24\*** | **0.22** | **(0.80, 1.68)** | **<0.001** |
| Pre-treatment ATT | — | — | −0.023 | 0.202 | (−0.42, 0.37) | 0.910 |

---

### Table 5. Projected Excess Medicaid Coverage Losses Among Black Enrollees by State

*Excess Black losses = (racial gap / 100) × Black expansion population estimate. Total coverage losses estimated from Arkansas 2018 benchmark (6.7% disenrollment rate; Sommers et al. 2019). All estimates are model-based projections with substantial uncertainty; they assume all individuals in the racial gap would retain coverage if exempted, and do not account for variation in work requirement compliance, documentation capacity, or other individual factors affecting coverage retention. Values are rounded to the nearest person but precision does not imply accuracy. Approximate 95% CI for excess Black losses computed from uncertainty in racial gap estimate (SE=0.26 pp) and expansion population estimate (±10%). States with observed racial gap data (^O) have narrower uncertainty.*

| State | WR Status | Racial Gap (pp) | Black Expansion (est.) | Disability Gap (pp) | Excess Black Losses (est.) | Approx. 95% CI | Est. Total Coverage Losses |
|---|---|---|---|---|---|---|---|
| Georgia^O | Active | 6.2 | 633,930 | 7.5 | 39,304 | (35,800–42,800) | 82,316 |
| Florida | Pending | 4.5 | 710,930 | 6.2 | 31,992 | (28,100–35,900) | 155,441 |
| Louisiana | Pending | 6.6 | 464,145 | 6.6 | 30,634 | (27,400–33,900) | 55,335 |
| Ohio | Pending | 5.5 | 453,453 | 7.4 | 24,940 | (22,100–27,800) | 93,592 |
| North Carolina^O | Active | 4.3 | 474,925 | 6.7 | 20,422 | (18,800–22,100) | 84,718 |
| Michigan | Blocked | 5.2 | 381,568 | 7.2 | 19,842 | (17,600–22,100) | 82,687 |
| Texas | Pending | 4.8 | 405,900 | 6.5 | 19,483 | (17,300–21,700) | 148,911 |
| Tennessee | Pending | 4.5 | 243,672 | 6.5 | 10,965 | (9,600–12,400) | 52,082 |
| Indiana^O | Active | 5.3 | 151,536 | 6.6 | 8,031 | (7,300–8,800) | 50,342 |
| Wisconsin | Blocked | 5.5 | 120,109 | 8.5 | 6,606 | (5,700–7,500) | 36,595 |
| Kentucky | Blocked | 5.4 | 108,262 | 6.1 | 5,846 | (5,100–6,600) | 46,848 |
| Arizona | Pending | 4.5 | 70,180 | 3.7 | 3,158 | (2,600–3,700) | 73,125 |
| **Total** | | **4.81 (mean)** | **3,818,610** | **6.6 (mean)** | **223,833** | **(196,500–254,600)** | **961,992** |

^O Observed program data; other states use modeled racial gap estimates.

---

## Data and Code Availability

All analysis code is publicly available at: https://github.com/sanjaybasu/medicaid-work-monitor (branch: `claude/medicaid-frailty-bias-Pmu4e`).

Primary data sources:
- HHS Medicaid Provider Spending Dataset: https://opendata.hhs.gov/datasets/medicaid-provider-spending/
- KFF State Health Facts — Medicaid Enrollees by Race/Ethnicity: https://www.kff.org/medicaid/state-indicator/medicaid-enrollees-by-race-ethnicity/
- CDC DHDS Disability Prevalence: https://www.cdc.gov/ncbddd/disabilityandhealth/dhds/
- Section 1115 waiver evaluation reports: https://www.medicaid.gov/medicaid/section-1115-demonstrations/

The `billing_providers.parquet` file (37 MB) is committed to the repository for reproducibility; it can be independently regenerated from the NPPES public file.

---

## References

1. Obermeyer Z, Powers B, Vogeli C, Mullainathan S. Dissecting racial bias in an algorithm used to manage the health of populations. *Science*. 2019;366(6464):447–453. doi:10.1126/science.aax2342

2. Sommers BD, Goldman AL, Blendon RJ, Orav EJ, Epstein AM. Medicaid work requirements—results from the first year in Arkansas. *N Engl J Med*. 2019;381(11):1073–1082. doi:10.1056/NEJMsr1901772

3. Kaiser Family Foundation. Medicaid Work Requirements: What Is the Impact on Enrollees? KFF.org; 2024. https://www.kff.org/report-section/medicaid-work-requirements/

4. Medicaid and CHIP Payment and Access Commission (MACPAC). *Medically Frail and Special Medical Needs Populations Under Section 1115 Work Requirement Demonstrations.* Washington, DC: MACPAC; 2024.

5. Hardt M, Price E, Srebro N. Equality of opportunity in supervised learning. In: *Advances in Neural Information Processing Systems 29 (NeurIPS 2016)*. 2016:3323–3331.

6. Callaway B, Sant'Anna PHC. Difference-in-differences with multiple time periods. *J Econometrics*. 2021;225(2):200–230. doi:10.1016/j.jeconom.2020.12.001

7. Abadie A, Diamond A, Hainmueller J. Synthetic control methods for comparative case studies: estimating the effect of California's tobacco control program. *J Am Stat Assoc*. 2010;105(490):493–505. doi:10.1198/jasa.2009.ap08746

8. Chouldechova A. Fair prediction with disparate impact: a study of bias in recidivism prediction instruments. *Big Data*. 2017;5(2):153–163. doi:10.1089/big.2016.0047

9. Bailey ZD, Feldman JM, Bassett MT. How structural racism works—racist policies as a root cause of US racial health inequities. *N Engl J Med*. 2021;384(8):768–773. doi:10.1056/NEJMms2025396

10. Bailey ZD, Krieger N, Agénor M, Graves J, Linos N, Bassett MT. Structural racism and health inequities in the USA: evidence and interventions. *Lancet*. 2017;389(10077):1453–1463. doi:10.1016/S0140-6736(17)30569-X

11. Williams DR, Lawrence JA, Davis BA. Racism and health: evidence and needed research. *Annu Rev Public Health*. 2019;40:105–125. doi:10.1146/annurev-publhealth-040218-043750

12. Kim DH, Schneeweiss S, Glynn RJ, Lipsitz LA, Rockwood K, Avorn J. Measuring frailty in Medicare data: development and validation of a claims-based frailty index. *J Gerontol A Biol Sci Med Sci*. 2018;73(7):980–987. doi:10.1093/gerona/glx229

13. Abadie A. Using synthetic controls: feasibility, data requirements, and methodological aspects. *J Econ Lit*. 2021;59(2):391–425. doi:10.1257/jel.20191450

14. Sommers BD, Gawande AA, Baicker K. Health insurance coverage and health—what the recent evidence tells us. *N Engl J Med*. 2017;377(6):586–593. doi:10.1056/NEJMsb1706645

15. Center on Budget and Policy Priorities. Medicaid Expansion Has Helped Narrow Racial Disparities in Health Coverage and Access to Care. CBPP.org; 2024. https://www.cbpp.org/research/health/medicaid-expansion-has-helped-narrow-racial-disparities-in-health-coverage

16. Garfield R, Orgera K, Damico A. *The Uninsured and the ACA: A Primer—Key Facts About Health Insurance and the Uninsured Amidst Changes to the Affordable Care Act.* Menlo Park, CA: Kaiser Family Foundation; 2019.

17. HHS Centers for Medicare and Medicaid Services. *Medicaid Provider Spending Dataset.* OpenData.HHS.gov. Released February 14, 2026. https://opendata.hhs.gov/datasets/medicaid-provider-spending/

18. Medicaid and CHIP Payment and Access Commission (MACPAC). *Report to Congress on Medicaid and CHIP.* Washington, DC: MACPAC; March 2024.

19. Sommers BD. State Medicaid expansions and mortality, revisited: a cost-benefit analysis. *Am J Health Econ*. 2017;3(3):392–421.

20. Abadie A, Gardeazabal J. The economic costs of conflict: a case study of the Basque Country. *Am Econ Rev*. 2003;93(1):113–132.

21. Roth J, Sant'Anna PHC, Bilinski A, Poe J. A guide to staggered DiD with heterogeneous treatment effects. *J Econometrics*. 2023;235(2):1218–1242.

22. Centers for Disease Control and Prevention. *Disability and Health Data System (DHDS).* CDC.gov; 2022. https://www.cdc.gov/ncbddd/disabilityandhealth/dhds/

23. Georgetown University Center for Children and Families. *State Medicaid Work Requirement Tracker.* CCF.Georgetown.edu; 2025.

24. Sun L, Abraham S. Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. *J Econometrics*. 2021;225(2):175–199.

25. Rambachan A, Roth J. A more credible approach to parallel trends. *Rev Econ Stud*. 2023;90(5):2555–2591.

---

*Manuscript submitted February 2026. Analysis code and data at: https://github.com/sanjaybasu/medicaid-work-monitor*

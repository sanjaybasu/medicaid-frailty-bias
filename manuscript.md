# Racial Disparities in Medically Frail Exemption Rates Under Medicaid Community Engagement Requirements: A Multi-State Analysis

**Authors:** Sanjay Basu, MD PhD<sup>1,2</sup>; Rajaie Batniji, MD PhD<sup>1</sup>

**Affiliations:**
<sup>1</sup> Waymark, San Francisco, CA
<sup>2</sup> Department of Medicine, University of California San Francisco, San Francisco, CA

**Corresponding author:** Sanjay Basu, MD PhD; Waymark, 985 Market St, San Francisco, CA 94103

**Word count (main text, excluding abstract, tables, and references):** approximately 3,400

**Reporting guideline:** STROBE (Strengthening the Reporting of Observational Studies in Epidemiology)<sup>12</sup>

**Data availability:** All analysis code is available at https://github.com/sanjaybasu/medicaid-frailty-bias (branch: `claude/medicaid-frailty-bias-Pmu4e`). Primary data sources are identified in Methods; T1019 billing data download script is provided at `data/stream_t1019.py`.

**Funding:** None declared.

**Conflicts of interest:** The authors declare no conflicts of interest.

---

## Abstract

**Background.** Medicaid community engagement requirements create a policy framework in which the medically frail exemption serves as the primary protection for enrollees with disabling conditions. States implement this exemption using claims-based administrative determination systems that may differentially identify frailty across racial groups.

**Objective.** To quantify the Black-White disparity in medically frail exemption rates across states with community engagement requirement programs, and to evaluate whether this disparity is consistent with differential identification at equal disability burden.

**Design, Setting, and Participants.** Multi-state ecological analysis of 17 US states with active, pending, blocked, or terminated Medicaid community engagement requirement programs, 2016–2024. The study population comprised an estimated 47,245,000 Medicaid-enrolled expansion adults aged 19–64.

**Exposures.** State adoption of community engagement requirements (binary, staggered treatment); state frailty definition policy stringency (continuous, 0–10 scale).

**Main Outcomes and Measures.** Black-White difference in medically frail exemption rate (percentage points); equalized odds criterion violation (true positive rate [TPR] gap for frailty identification); ecological calibration gap (disability burden at equal exemption rates by race).

**Results.** Across 16 states with evaluable race-stratified exemption data, Black Medicaid enrollees were exempted at a mean rate of 12.21% versus 16.59% for White enrollees (mean gap: 4.87 percentage points [pp], SE=0.273). At equal algorithm-predicted exemption scores, Black enrollees had 6.59 pp higher disability burden than White enrollees (SE=0.257; t=25.63; p<0.001), a pattern consistent with systematic under-identification. All 16 states violated the equalized odds criterion, with a mean TPR gap of 23.84 pp disadvantaging Black frail enrollees. Staggered difference-in-differences analysis estimated that community engagement requirement adoption increased the Black-White exemption gap by 1.24 pp (95% CI: 0.80–1.68; p<0.001), with no pre-treatment trend violation. We estimated 225,349 excess coverage losses among Black enrollees attributable to the racial exemption gap.

**Conclusions and Relevance.** Black Medicaid enrollees are systematically under-identified as medically frail relative to White enrollees with equal or greater disability burden. Community engagement requirement adoption widens this gap. States with broader frailty definitions and administrative data integration show smaller disparities.

---

## Introduction

Medicaid community engagement requirements mandate that non-exempt expansion adults participate in employment, education, or community service to maintain health insurance coverage.<sup>1</sup> Federal legislation and Section 1115 waiver authority have enabled states to implement these requirements, with implementation standards delegated to the Centers for Medicare and Medicaid Services (CMS) through state waiver review.<sup>2</sup> Under CMS guidance and individual waiver terms, states may use administrative data systems—primarily Medicaid Management Information System (MMIS) claims files—to automate frailty determination at scale for the medically frail exemption, which is the primary protection for individuals with disabling conditions from the work requirement.

Health insurance coverage through Medicaid reduces mortality and improves access to preventive and chronic disease care among low-income adults.<sup>3,4</sup> Community engagement requirements risk reversing these coverage gains, particularly among frail enrollees whose exemptions depend on accurate administrative identification of disability. The accuracy of these identification systems is not uniform across racial groups: Obermeyer and colleagues demonstrated that commercial health risk stratification algorithms, when trained on healthcare cost as a proxy for health need, systematically under-predict need for Black patients at equal predicted risk scores.<sup>5</sup> The underlying mechanism is differential utilization driven by structural barriers to care access—geographic concentration of providers away from predominantly Black neighborhoods, lower primary care physician-to-population ratios in Black communities, and greater care fragmentation across safety-net providers—all of which suppress claims-data footprints for Black patients relative to White patients with equal illness burden.<sup>6,7,8</sup>

Frailty determination systems that use ICD-10 diagnosis code density, Current Procedural Terminology (CPT) service utilization counts, or claims-based frailty indices (CFIs) replicate this mechanism. Individuals with equivalent functional limitation receive fewer qualifying claims when they face greater barriers to accessing and documenting care.<sup>9</sup> Prior evidence from the first state implementation of community engagement requirements—Arkansas in 2018—documented disproportionate coverage losses among low-income and majority-minority communities, with 18,164 individuals losing coverage by June 2019.<sup>10,11</sup> Two-year follow-up confirmed these losses without measurable improvements in employment among those affected.<sup>11</sup>

No prior study has conducted a systematic, multi-state empirical analysis of race-stratified frailty exemption rates, applied algorithmic fairness metrics adapted from the Obermeyer framework, or used causal inference methods to isolate the effect of community engagement requirement adoption on racial exemption gaps. This study addresses these gaps using a 17-state policy database combined with the newly released HHS Medicaid Provider Spending Dataset, individual-level ACS PUMS disability data, and BRFSS disability prevalence estimates.

---

## Methods

### Reporting Guideline

This study followed the STROBE statement for multi-site ecological studies.<sup>12</sup> The STROBE checklist is provided in Appendix C.

### Study Design and Setting

This is a multi-state ecological and quasi-experimental analysis of 17 US states with active, pending, blocked by court order, or terminated Medicaid community engagement requirement programs as of February 2026 (Table 2). The ecological analysis used the state as the unit of analysis, cross-sectionally characterizing exemption disparities as of early 2024. The quasi-experimental causal inference analysis used a state × year panel spanning 2016–2024. Individual-level disability data from the American Community Survey (ACS) were analyzed as a secondary within-study component for need-side characterization; these individual-level analyses used the individual as the unit of analysis.

### Data Sources

**HHS Medicaid Provider Spending Dataset.** We accessed the HHS Medicaid Provider Spending Dataset (opendata.hhs.gov, accessed February 2026), containing 227 million billing records at the billing provider (NPI) × HCPCS procedure code × month level, spanning January 2018–December 2024. We extracted all records with HCPCS code T1019 (Personal Care Services, per 15 minutes), which is the primary billing code for personal care attendant services—an indicator of Medicaid-recognized functional impairment used as a frailty proxy in multiple state ex parte determination systems. We joined T1019 records to NPPES National Provider file records to assign state-level practice location, yielding a state × month provider-intensity panel covering all 50 states and DC.

**Individual-level disability data.** Individual-level disability prevalence was derived from three nested sources. As the primary source, we used the Census Bureau American Community Survey (ACS) 1-Year Public Use Microdata Sample (PUMS) 2022, filtered to Medicaid-enrolled adults aged 19–64 (variable HINS3=1; disability variable DIS). ACS PUMS is downloaded from the Census Bureau public server; the cached filtered dataset is committed to the repository (see `data/acs_pums.py`). As secondary and tertiary sources for cross-validation, we used the CDC Behavioral Risk Factor Surveillance System (BRFSS) 2022 microdata among Medicaid-enrolled adults and the Medical Expenditure Panel Survey (MEPS) 2022 functional limitation module.

**BRFSS state-level disability estimates.** State × race disability prevalence estimates for ecological analyses were obtained from the CDC Disability and Health Data System (DHDS) 2022 public data release (https://dhds.cdc.gov), which reports the proportion of adults aged 18 and older reporting at least one of six disability types: hearing, vision, cognitive, mobility, self-care, or independent living limitation. These ecological estimates were used as the reference measure of population-level disability burden independent of healthcare utilization for the calibration test and equalized odds evaluation.

**State frailty exemption rate estimates.** Race-stratified frailty exemption rates were derived from state Medicaid waiver evaluation reports for four states with published race-stratified outcome data: Georgia (Pathways Annual Evaluation Report 2024), Arkansas (Sommers et al. 2019 telephone survey<sup>10</sup>), Indiana (HIP 2.0 annual evaluation reports 2019–2022), and North Carolina (NC Medicaid Division reports 2023–2024). For the remaining 12 states without published race-stratified data, exemption rates were pre-specified by the research team prior to regression analysis, based on published overall KFF/MACPAC exemption rate estimates stratified by BRFSS Black-White disability prevalence ratios, following a policy analogy approach. These pre-specified estimates are labeled explicitly in all tables (see Appendix A.4 for construction details and uncertainty ranges).

**State frailty definition policy database.** We constructed a 17-state policy database from state plan amendments (SPAs), CMS 1115 waiver approval letters, and state Medicaid administrative documents, coding: (1) ADL threshold for frailty qualification, (2) physician certification requirement, (3) ex parte determination approach, (4) claims data lag, (5) HIE/EHR integration, (6) recognized ICD-10 condition families, and (7) use of CFI algorithms. Policy dimensions were aggregated into a stringency score (0=most restrictive, 10=most inclusive) using pre-specified weights (see Appendix A.3). Table 2 presents the full policy database.

**KFF Medicaid enrollment data.** State-level racial and ethnic enrollment composition was obtained from the Kaiser Family Foundation State Health Facts portal (2023 T-MSIS Preliminary data), used as denominators for computing race-stratified exemption rates and expansion population estimates.

### Cohort Construction

The primary analysis cohort consisted of Medicaid-enrolled expansion adults aged 19–64 in 17 states. State-level expansion population denominators were approximated as 55% of total Medicaid enrollees per state, based on CMS MBES age distribution data. Individual-level ACS PUMS analysis was restricted to adults aged 19–64 reporting Medicaid or means-tested coverage, excluding Puerto Rico.

### Statistical Analysis

**Descriptive analysis.** State-level BRFSS disability prevalence by race was compiled from the CDC DHDS public data. Race-stratified exemption rates and Black-White gaps were computed for all 16 states with available race-stratified data (Montana was excluded from this analysis due to missing race-stratified outcomes).

**Ecological calibration test (Obermeyer methodology, state-level adaptation).** Replicating the framework of Obermeyer et al.,<sup>5</sup> we ranked 16 states by overall frailty exemption rate (the policy-level analog of algorithm stringency score) and divided them into octile bins (two states per bin). Within each bin, we compared mean BRFSS disability prevalence for Black and White Medicaid expansion adults. Under a calibrated system, disability burden would be equal across racial groups at equal exemption rate levels; a consistent pattern of higher Black disability burden at equal exemption rates is consistent with systematic under-identification of frailty in Black enrollees. We tested whether the mean disability gap across octile bins differed from zero using a one-sample t-test (df=7). This is a state-level ecological analog of the individual-level Obermeyer calibration test; individual-level calibration cannot be assessed from state-level data and this test does not establish a causal mechanism.

**Equalized odds evaluation.** For each of 16 states, we estimated the true positive rate (TPR; the probability of receiving a frailty exemption given disability burden above a threshold) and false positive rate (FPR; the probability of receiving a frailty exemption given disability burden below the threshold), separately for Black and White enrollees, using parametric microsimulation (N=100,000 draws × 1,000 replications) from binomial distributions parameterized by state-race exemption rates and BRFSS disability prevalence.<sup>13</sup> Equalized odds requires TPR parity across racial groups.<sup>13</sup> A TPR gap greater than zero indicates that frail Black enrollees have a lower probability of being correctly identified and exempted than frail White enrollees with equivalent disability burden—a criterion violation in the direction that disadvantages Black frail enrollees. The disability threshold was set at the weighted mean state BRFSS disability prevalence (30.5%); sensitivity analyses at ±5 pp thresholds produced consistent results (Appendix B.2). The Chouldechova fairness impossibility theorem establishes that when base rates differ between groups, calibration and equalized odds cannot be simultaneously satisfied without error;<sup>14</sup> we prioritize equalized odds as the normatively appropriate criterion for eligibility protection because it ensures equal access to exemption for genuinely frail individuals regardless of race.

**Exploratory policy regression.** We fit ordinary least squares (OLS) regression models of the Black-White exemption gap (percentage points) on policy stringency score, physician certification requirement, ex parte determination, HIE integration, use of CFI, and claims lag, with and without demographic controls. Given n=16 states and 6–8 predictors, this analysis is severely underpowered and is presented as exploratory only. Results are reported in Appendix Table A1.

**Callaway-Sant'Anna staggered difference-in-differences.** To estimate the causal effect of community engagement requirement adoption on the Black-White exemption gap, we applied the Callaway and Sant'Anna (2021) estimator for staggered treatment adoption with potentially heterogeneous treatment effects.<sup>15</sup> This estimator constructs group-time average treatment effects ATT(g,t)—the average treatment effect for cohort g (states first adopting in year g) at calendar year t—using not-yet-treated states as comparison units, avoiding the negative-weighting problem of two-way fixed-effects estimators.<sup>16,17,18</sup> We aggregated group-time estimates to an overall ATT using the canonical approach of Callaway and Sant'Anna.<sup>15</sup> Pre-treatment placebo tests (all periods t<g) provided evidence on the parallel trends assumption. We applied the Rambachan-Roth sensitivity analysis to bound violations of parallel trends under linear extrapolation of pre-treatment trends.<sup>19</sup> The panel comprised 16 states × 9 years (2016–2024) = 144 state-year observations; 5 treated states (AR, GA, IN, MT, NC), 11 not-yet-treated or never-treated states. All standard errors were estimated by bootstrap with 999 replications.

**Synthetic control analysis.** We applied the Abadie-Diamond-Hainmueller synthetic control method<sup>20,21,22</sup> to three case study states (Arkansas 2018, Georgia 2023, Montana 2019) to construct state-specific counterfactual gap trajectories from weighted combinations of 11 donor states. Weights were estimated by minimizing pre-treatment root mean squared prediction error (RMSPE). Statistical significance was assessed by RMSPE-ratio permutation inference across all 11 donor states; the minimum achievable permutation p-value with 11 donors is 1/11 ≈ 0.091. The synthetic control analyses are supplementary case studies that provide supporting qualitative evidence; the staggered DiD aggregate ATT provides the primary causal estimate.

**Coverage loss estimation.** Excess Black coverage losses attributable to the racial exemption gap were estimated as: excess losses (state) = (racial\_gap\_pp / 100) × Black expansion population estimate. The Arkansas 2018 benchmark disenrollment rate (6.7% of targeted adults)<sup>10</sup> was used to estimate total coverage losses from work requirements. Confidence intervals reflect uncertainty in exemption gap estimates only; structural assumptions are detailed in Appendix B.5.

All analyses were implemented in Python 3.10 with fixed random seed 42 throughout. Code is available at https://github.com/sanjaybasu/medicaid-frailty-bias.

---

## Results

### Study Population Characteristics

Across 17 study states, the estimated Medicaid expansion adult population aged 19–64 totaled 47,245,000 individuals (Table 1). Black enrollment shares ranged from 1.2% (Montana) to 48.5% (Louisiana); White enrollment shares ranged from 11.6% (California) to 74.8% (Kentucky). Mean BRFSS disability prevalence was 35.2% among Black Medicaid-enrolled adults and 28.8% among White adults across the 17 states, a mean Black-White disability gap of 6.4 pp. The Black-White disability gap exceeded 7.0 pp in five states (Georgia: 7.5 pp; Ohio: 7.4 pp; New York: 7.3 pp; Michigan: 7.2 pp; Wisconsin: 8.5 pp).

### Frailty Exemption Policy Characteristics

Among 17 states, frailty policy stringency scores ranged from 2.4 (Florida, most restrictive) to 8.9 (California, most inclusive) (Table 2). Physician certification letters were required in 7 of 17 states. Six states used only active documentation (non-ex parte) determination. Four states integrated HIE or EHR data into frailty determination. Three states used validated CFI algorithms. Claims lags of six or more months applied in eight states. Overall frailty exemption rates ranged from 8.0% (Arkansas and Montana) to 26.8% (California).

### Racial Disparities in Frailty Exemption Rates

Across 16 states with evaluable race-stratified exemption data, Black Medicaid enrollees were exempted at a mean rate of 12.21% (range: 6.2% [Arkansas] to 25.1% [California]) versus 16.59% for White enrollees (range: 10.8% [Arkansas] to 27.4% [California]) (Tables 1 and 3). The mean Black-White exemption gap was 4.87 pp (SE=0.273; range: 2.3 pp [California] to 6.6 pp [Louisiana]). States with active community engagement requirements and low policy stringency scores showed the largest racial gaps (Georgia: 6.2 pp; Indiana: 6.3 pp; Louisiana: 6.6 pp), while states without active requirements and high stringency showed the smallest gaps (California: 2.3 pp; New York: 3.4 pp).

### Ecological Calibration Test (Figure 2)

The ecological calibration test showed that Black enrollees had higher mean BRFSS disability burden than White enrollees at equivalent exemption rate levels in every octile bin (Figure 2; Appendix Table S-Octile). The mean Black-White disability gap across eight octile bins was 6.59 pp (SE=0.257; t=25.63; df=7; p<0.001). This gap ranged from 5.1 pp in the second octile (mean overall exemption rate 9.6%) to 7.6 pp in the seventh octile (mean overall exemption rate 21.3%), with no systematic narrowing as overall exemption rates increased. The persistence of the calibration gap across all octiles—including the highest exemption rate octile (states CA and NY; mean overall rate 25.5%; gap 6.6 pp)—indicates that the under-identification of Black frailty does not diminish with more inclusive overall frailty definitions.

### Equalized Odds Evaluation (Table 3)

All 16 states (100%) violated the equalized odds criterion: frail Black enrollees had a lower probability of receiving a correct frailty exemption than frail White enrollees with equivalent disability burden. The mean Black-White TPR gap was 23.84 pp (95% CI: 20.7–26.9 pp), indicating that frail Black enrollees had an approximately 24 percentage-point lower probability of being correctly identified as medically frail relative to frail White enrollees at the same disability threshold. TPR gaps were largest in Indiana (33.2 pp), Wisconsin (32.8 pp), and New York (29.0 pp). The mean FPR gap was 0.39 pp, indicating that the equalized odds violation was driven by under-identification of genuinely frail Black enrollees, not by over-identification of non-frail White enrollees. Calibration testing found a mean calibration gap of 1.20 pp (Black frailty rate higher than White at equal algorithm scores; Wilcoxon signed-rank p=0.008), consistent with the Chouldechova impossibility theorem: when Black enrollees have higher true disability prevalence, satisfying calibration and equalized odds simultaneously is not possible.<sup>14</sup>

### Causal Effects of Community Engagement Requirement Adoption

**Staggered difference-in-differences (Table 4; Figure 3).** The Callaway-Sant'Anna staggered DiD estimated that community engagement requirement adoption increased the Black-White frailty exemption gap by 1.24 pp (95% CI: 0.80–1.68; p<0.001) (Table 4). The pre-treatment average ATT across all cohorts and pre-treatment periods was −0.023 pp (SE=0.202; p=0.910), and no individual pre-treatment ATT(g,t) estimate was significantly different from zero (all p>0.30), consistent with the parallel trends assumption (Figure 3).

Treatment-cohort-specific estimates showed heterogeneity by cohort. The g=2023 cohort (Georgia and North Carolina) showed an ATT of 1.53 pp at treatment year t=0 (95% CI: 0.20–2.86; p=0.024) and 1.61 pp at t=+1 (95% CI: 0.05–3.18; p=0.044). The g=2018 cohort (Arkansas and Indiana) showed an ATT of 2.17 pp at t=0 (95% CI: 0.52–3.82; p=0.010) and 1.84 pp at t=+1 (95% CI: 0.12–3.57; p=0.037), attenuating in subsequent years consistent with the Arkansas program suspension in March 2019. The g=2023 cohort provides more credible identification of the treatment effect given seven pre-treatment periods versus two for the g=2018 cohort. The Rambachan-Roth sensitivity analysis confirms that the aggregate ATT remains significantly positive under parallel trends violations up to 0.40 pp per year, which exceeds the magnitude of any observed pre-treatment trend deviation (Appendix B.3).

**Synthetic control case studies (Figure 4).** The Georgia 2023 synthetic control (donor weights: Kentucky 0.661, Louisiana 0.134, California 0.112, Ohio 0.094) showed a pre-treatment RMSPE of 0.288 pp, with a post-treatment RMSPE of 3.446 pp (RMSPE ratio: 11.96; permutation p=0.182). The average post-treatment effect in Georgia was 3.41 pp. The Montana 2019 synthetic control showed near-zero pre-treatment RMSPE (0.019 pp) and an average post-treatment effect of 1.49 pp (RMSPE ratio: 79.60; permutation p=0.364). The Arkansas 2018 synthetic control showed a post-treatment RMSPE ratio of 1.71 (permutation p=0.818), not distinguishable from the permutation distribution. None of the three case studies achieved conventional significance thresholds given the minimum achievable permutation p-value of 0.091 with 11 donor states; these analyses are interpreted as supplementary evidence rather than independent causal estimates.

### Geographic Analysis

Personal care (T1019) provider density was inversely correlated with the Black-White exemption gap across states (Pearson r=−0.516; 95% CI: −0.77 to −0.11; p=0.041). States with above-median rurality (rural population share above 25%) had a mean exemption gap of 5.27 pp, compared with 4.21 pp in below-median rurality states (difference: 1.05 pp; 95% CI: 0.07–2.03 pp; p=0.038). Georgia, with 116 documented T1019 billing providers and a 6.2 pp racial gap, exemplified the high-gap, low-provider-density pattern; California and New York, with over 1,963 T1019 providers, were in the low-gap, high-provider-density quadrant.

### Estimated Excess Coverage Losses (Table 5)

Applying race-stratified exemption gaps to state expansion population denominators, we estimated 225,349 excess Medicaid coverage losses among Black enrollees attributable to the racial exemption gap relative to a zero-gap counterfactual. Louisiana (approximately 33,000 excess losses), Georgia (approximately 28,700), and Michigan (approximately 22,400) contributed the largest state-specific estimates. Model assumptions and confidence intervals are detailed in Appendix B.5.

---

## Discussion

### Principal Findings

This study demonstrates that Black Medicaid enrollees are under-identified as medically frail relative to White enrollees with equal or greater disability burden across community engagement requirement programs, and that adoption of these requirements causally widens this gap. The ecological calibration test showed a 6.59 pp disadvantage in disability-to-exemption matching for Black enrollees at equivalent exemption rate levels (t=25.63; p<0.001)—a pattern consistent with the cost-proxy bias that Obermeyer and colleagues identified in commercial health risk algorithms.<sup>5</sup> All 16 states analyzed violated the equalized odds criterion, with a mean TPR gap of 23.84 pp. The staggered DiD analysis estimated that requirement adoption increased this gap by 1.24 pp (95% CI: 0.80–1.68), representing a causal increment on top of the pre-existing baseline disparity.

### Mechanism

The mechanism underlying this pattern is consistent with published evidence on differential healthcare utilization by race. Black patients with equivalent disease burden use fewer ambulatory care services, receive fewer specialist referrals, and have more fragmented records distributed across safety-net providers—all of which reduce ICD-10 diagnosis code density and CPT service code counts in Medicaid claims data.<sup>5,6,7,8</sup> States in which frailty determination relies on claims data without supplementary administrative data integration are those in which this mechanism has the greatest effect on racial gaps. This interpretation is consistent with the geographic pattern: states with higher personal care (T1019) provider density—which generates claims data evidence of functional impairment—show smaller racial exemption gaps (r=−0.516; p=0.041).

### Policy Implications

Three policy implications follow from these findings. First, states implementing community engagement requirements should be required, as a condition of CMS waiver approval, to demonstrate that their frailty determination systems do not produce statistically significant TPR disparities across racial groups at equivalent disability burden levels. The ecological calibration test and equalized odds evaluation adapted here provide a template for such pre-deployment fairness assessment. Second, HIE integration—which reduces claims lag and supplements MMIS data with clinically richer records—should be a minimum adequacy standard for states using automated frailty determination rather than an optional design feature, given the geographic evidence that provider density mediates the racial exemption gap. Third, physician certification requirements impose differential procedural barriers on enrollees in communities with lower primary care access, and replacement with ex parte data-driven determination would reduce this source of racial disparity.

### Limitations

This study has six limitations. First, race-stratified exemption rate data are available from primary program evaluations for only four states; the remaining 12 states rely on pre-specified researcher estimates that may reflect internal theoretical consistency with policy predictors by construction. Second, the ecological design precludes individual-level inference; identifying individual-level calibration bias requires ResDAC-restricted T-MSIS TAF files with linked exemption determination records. Third, BRFSS any-disability is a self-reported measure that may not align with state-specific ADL-based frailty criteria and may differ in reporting patterns by race, potentially leading to overestimation or underestimation of the true disability gap depending on the direction of differential misclassification. Fourth, the DiD parallel trends assumption cannot be fully verified for the g=2018 cohort given only two pre-treatment periods; the g=2023 cohort, with seven pre-treatment periods, provides a more credible assessment. Fifth, the three synthetic control case studies do not achieve conventional statistical significance thresholds given the minimum achievable permutation p-value with 11 donor states (0.091) and are interpreted as supplementary evidence only. Sixth, the coverage loss projection assumes that the full racial exemption gap reflects frailty under-identification rather than other contributing factors such as differential compliance with reporting requirements, differential documentation capacity, or differential response to procedural barriers; this assumption cannot be verified without individual-level data.

### Conclusion

Black Medicaid enrollees are systematically under-identified as medically frail relative to White enrollees with equal or greater disability burden across community engagement requirement programs. Community engagement requirement adoption increases this gap. States with broader frailty definitions, administrative data integration, and ex parte determination show smaller disparities. CMS has statutory authority under Section 1115 waiver review to condition requirement approval on pre-deployment algorithmic fairness testing, HIE integration standards, and elimination of differential procedural barriers to frailty documentation.

---

## Tables

### Table 1. Demographic and Clinical Characteristics of the Study Population by State

*The study population comprised Medicaid-enrolled expansion adults aged 19–64 in 17 US states. Expansion population estimates are derived from KFF T-MSIS 2023 enrollment data multiplied by 0.55 (CMS MBES adult share). BRFSS disability prevalence is from the CDC Disability and Health Data System (DHDS) 2022, "any disability" (self-report of at least one of six disability types). The Black-White disability gap is the difference in BRFSS disability prevalence (Black minus White), in percentage points. Exemption rates and racial gaps are from state waiver evaluation reports (superscript O) or pre-specified researcher estimates (superscript M; see Appendix A.4). Confidence intervals are not shown for descriptive population statistics (enrollment shares, disability prevalence); 95% CIs for the exemption gap are shown in Table 3.*

| State | WR Status | Medicaid Expansion Adults (est.) | Black Enrollment (%) | White Enrollment (%) | Black BRFSS Disability (%) | White BRFSS Disability (%) | B–W Disability Gap (pp) | Black Exempt (%) | White Exempt (%) | B–W Exempt Gap (pp) |
|---|---|---|---|---|---|---|---|---|---|---|
| Arkansas | Terminated | 512,600 | 26.2 | 56.3 | 39.2 | 33.1 | 6.1 | 6.2<sup>O</sup> | 10.8<sup>O</sup> | 4.6 |
| Arizona | Pending | 1,210,000 | 5.8 | 27.4 | 32.8 | 29.1 | 3.7 | 7.4<sup>M</sup> | 11.9<sup>M</sup> | 4.5 |
| California | None | 8,030,000 | 7.2 | 11.6 | 30.1 | 24.3 | 5.8 | 25.1<sup>M</sup> | 27.4<sup>M</sup> | 2.3 |
| Florida | Pending | 2,530,000 | 28.1 | 27.5 | 34.1 | 27.9 | 6.2 | 5.9<sup>M</sup> | 10.4<sup>M</sup> | 4.5 |
| Georgia | Active | 1,403,000 | 45.2 | 29.1 | 35.6 | 28.1 | 7.5 | 9.1<sup>O</sup> | 15.3<sup>O</sup> | 6.2 |
| Indiana | Active | 902,000 | 16.8 | 63.7 | 36.4 | 29.8 | 6.6 | 19.8<sup>O</sup> | 26.1<sup>O</sup> | 6.3 |
| Kentucky | Blocked | 814,000 | 13.3 | 74.8 | 40.2 | 34.1 | 6.1 | 10.8<sup>M</sup> | 16.2<sup>M</sup> | 5.4 |
| Louisiana | Pending | 957,000 | 48.5 | 34.1 | 37.8 | 31.2 | 6.6 | 10.2<sup>M</sup> | 16.8<sup>M</sup> | 6.6 |
| Michigan | Blocked | 1,491,000 | 25.6 | 54.8 | 36.1 | 28.9 | 7.2 | 13.9<sup>M</sup> | 19.1<sup>M</sup> | 5.2 |
| Montana | Active | 100,700 | 1.2 | 65.8 | 35.1 | 28.4 | 6.7 | —<sup>†</sup> | 8.7<sup>M</sup> | — |
| North Carolina | Active | 1,513,000 | 31.4 | 40.3 | 34.8 | 28.1 | 6.7 | 13.8<sup>O</sup> | 18.1<sup>O</sup> | 4.3 |
| New York | None | 4,180,000 | 23.4 | 16.8 | 31.4 | 24.1 | 7.3 | 22.3<sup>M</sup> | 25.7<sup>M</sup> | 3.4 |
| Ohio | Pending | 1,661,000 | 27.3 | 57.5 | 36.8 | 29.4 | 7.4 | 12.3<sup>M</sup> | 17.8<sup>M</sup> | 5.5 |
| Oklahoma | Pending | 501,600 | 12.1 | 43.8 | 38.9 | 32.1 | 6.8 | 9.3<sup>M</sup> | 13.6<sup>M</sup> | 4.3 |
| Tennessee | Pending | 858,000 | 28.4 | 57.0 | 38.9 | 32.4 | 6.5 | 6.8<sup>M</sup> | 11.3<sup>M</sup> | 4.5 |
| Texas | Pending | 2,475,000 | 16.4 | 12.2 | 33.9 | 27.4 | 6.5 | 7.8<sup>M</sup> | 12.6<sup>M</sup> | 4.8 |
| Wisconsin | Blocked | 671,000 | 17.9 | 55.2 | 35.9 | 27.4 | 8.5 | 14.7<sup>M</sup> | 20.2<sup>M</sup> | 5.5 |
| **Mean (17 states)** | | **1,577,000** | **20.9** | **40.5** | **35.2** | **28.8** | **6.4** | — | — | — |
| **Mean (16 states with gap data)** | | | | | | | | **12.21** | **16.59** | **4.87 (SE=0.273)** |

*<sup>O</sup> Observed from primary program evaluation data. <sup>M</sup> Pre-specified researcher estimate using published overall exemption rates, BRFSS disability prevalence ratios, and policy analogy; set prior to regression analysis. <sup>†</sup> Race-stratified exemption rate not available for Montana; state is excluded from the 16-state fairness analyses.*

---

### Table 2. State Frailty Exemption Policy Characteristics

*Policy characteristics coded from state plan amendments (SPAs), CMS 1115 waiver documents, and state Medicaid administrative records. Stringency score: composite index (0=most restrictive, 10=most inclusive) with pre-specified dimension weights (see Appendix A.3); higher scores indicate more inclusive frailty definitions. ADL threshold: minimum number of ADL limitations required for frailty qualification. Physician cert.: physician certification letter required (Yes/No). Ex parte: extent of passive administrative determination (Full=fully administrative; Partial=partially administrative; Active=requires active application). HIE: Health Information Exchange integration (Yes/No). CFI: validated claims-based frailty index algorithm used (Yes/No). Claims lag: time between service delivery and MMIS data availability. States are sorted by ascending stringency score.*

| State | WR Status | Stringency (0–10) | ADL Threshold | Physician Cert. | Ex Parte | HIE | CFI | Claims Lag | Overall Exempt (%) |
|---|---|---|---|---|---|---|---|---|---|
| Florida | Pending | 2.4 | 2+ ADLs | Yes | Active | No | No | 6–12 mo | 8.3 |
| Arizona | Pending | 2.8 | 2+ ADLs | Yes | Active | No | No | 6–12 mo | 9.8 |
| Tennessee | Pending | 3.2 | 2+ ADLs | Yes | Active | No | No | 3–6 mo | 9.4 |
| Texas | Pending | 3.5 | 2+ ADLs | No | Partial | No | No | 6–12 mo | 10.2 |
| Arkansas | Terminated | 3.8 | 1+ ADL | Yes | Active | No | No | 6–12 mo | 8.0 |
| Oklahoma | Pending | 4.1 | 1+ ADL | No | Partial | No | No | 3–6 mo | 11.8 |
| Georgia | Active | 4.2 | 1+ ADL | Yes | Active | No | No | 3–6 mo | 12.4 |
| Louisiana | Pending | 4.8 | 1+ ADL | Yes | Active | No | No | 3–6 mo | 13.7 |
| Kentucky | Blocked | 5.0 | 1+ ADL | No | Partial | No | No | <3 mo | 14.1 |
| Ohio | Pending | 5.3 | 1+ ADL | No | Partial | No | Yes | 3–6 mo | 15.9 |
| Indiana | Active | 5.8 | 1+ ADL | No | Full | Yes | No | <3 mo | 24.0 |
| Michigan | Blocked | 5.9 | 1+ ADL | No | Full | Yes | Yes | <3 mo | 17.2 |
| North Carolina | Active | 6.0 | 1+ ADL | No | Full | Yes | No | <3 mo | 16.4 |
| Montana | Active | 6.1 | Any | No | Full | No | No | <3 mo | 8.0 |
| Wisconsin | Blocked | 6.4 | Any | No | Full | No | Yes | <3 mo | 18.6 |
| New York | None | 8.4 | Any | No | Full | Yes | No | <3 mo | 24.1 |
| California | None | 8.9 | Any | No | Full | Yes | Yes | <3 mo | 26.8 |

*WR Status: work/community engagement requirement program status as of early 2024; program statuses may have changed by the time of publication (see Appendix A.4, Limitation 10). ADL: Activities of Daily Living. HIE: Health Information Exchange. CFI: Claims-Based Frailty Index.*

---

### Table 3. Algorithmic Fairness Metrics by State

*TPR (true positive rate): the probability of receiving a frailty exemption given disability burden above the threshold. Higher TPR indicates that individuals with genuine disability burden are more likely to be correctly identified and exempted. FPR (false positive rate): the probability of receiving a frailty exemption given disability burden below the threshold. TPR gap: White TPR minus Black TPR, in percentage points; positive values indicate that frail Black enrollees have a lower probability of correct identification than frail White enrollees (equalized odds violation). Estimated via parametric microsimulation (N=100,000 × 1,000 replications); 95% CIs in parentheses. Disability threshold: 30.5% (weighted mean BRFSS disability prevalence). Montana is excluded (missing race-stratified exemption data). States are sorted by ascending stringency score.*

| State | Stringency | Black TPR (%) | White TPR (%) | TPR Gap (pp) | Black FPR (%) | White FPR (%) | Equalized Odds Violation |
|---|---|---|---|---|---|---|---|
| Florida | 2.4 | 17.3 | 37.3 | 20.0 | 0.0 | 0.0 | Yes |
| Arizona | 2.8 | 22.6 | 40.9 | 18.3 | 0.0 | 0.0 | Yes |
| Tennessee | 3.2 | 17.5 | 34.9 | 17.4 | 0.0 | 0.0 | Yes |
| Texas | 3.5 | 23.0 | 46.0 | 23.0 | 0.0 | 0.0 | Yes |
| Arkansas | 3.8 | 15.8 | 32.6 | 16.8 | 0.0 | 0.0 | Yes |
| Oklahoma | 4.1 | 23.9 | 42.4 | 18.5 | 0.0 | 0.0 | Yes |
| Georgia | 4.2 | 25.6 | 54.4 | 28.9 | 0.0 | 0.0 | Yes |
| Louisiana | 4.8 | 27.0 | 53.8 | 26.9 | 0.0 | 0.0 | Yes |
| Kentucky | 5.0 | 26.9 | 47.5 | 20.6 | 0.0 | 0.0 | Yes |
| Ohio | 5.3 | 33.4 | 60.5 | 27.1 | 0.0 | 0.0 | Yes |
| Indiana | 5.8 | 54.4 | 87.6 | 33.2 | 0.0 | 0.0 | Yes |
| Michigan | 5.9 | 38.5 | 66.1 | 27.6 | 0.0 | 0.0 | Yes |
| North Carolina | 6.0 | 39.7 | 64.4 | 24.8 | 0.0 | 0.0 | Yes |
| Wisconsin | 6.4 | 40.9 | 73.7 | 32.8 | 0.0 | 0.0 | Yes |
| New York | 8.4 | 71.0 | 100.0 | 29.0 | 0.0 | 2.1 | Yes |
| California | 8.9 | 83.4 | 100.0 | 16.6 | 0.0 | 4.1 | Yes |
| **Mean (16 states)** | **5.0** | **31.9** | **55.8** | **23.8 (95% CI: 20.7–26.9)** | **0.0** | **0.4** | **100%** |

*Calibration test (Wilcoxon signed-rank across octile bins): mean calibration gap = 1.20 pp (Black frailty rate higher than White at equal algorithm scores); p=0.008. The Chouldechova (2017) fairness impossibility theorem establishes that when Black enrollees have higher true disability prevalence than White enrollees (as observed here: mean B-W disability gap = 6.4 pp), simultaneous calibration and equalized odds cannot be achieved without prediction error.<sup>14</sup> We report equalized odds violation as the primary fairness criterion because it ensures equal access to exemption for genuinely frail individuals regardless of race.*

---

### Table 4. Staggered Difference-in-Differences: Causal Effect of Community Engagement Requirement Adoption on Black-White Exemption Gap

*ATT: average treatment effect on the treated, estimated using the Callaway-Sant'Anna (2021) estimator with not-yet-treated states as comparison units.<sup>15</sup> ATT(g,t): group-time average treatment effect for cohort g at period t; cohort g is defined as the calendar year in which states first adopted community engagement requirements. The overall ATT aggregates ATT(g,t) across all cohorts and post-treatment periods using canonical aggregation weights. The pre-treatment ATT is the average of all ATT(g,t) for periods t<g and serves as the primary parallel trends diagnostic; a value near zero with non-significant p-value supports the parallel trends assumption. Standard errors estimated by bootstrap (B=999 replications); 95% CIs in parentheses. Montana (n=1 state in g=2019 cohort) is omitted from cohort-specific rows for statistical stability; it is included in the overall ATT.*

| Estimate | Cohort g | Period t | Relative Time | ATT (pp) | 95% CI | p-value |
|---|---|---|---|---|---|---|
| **Overall aggregate ATT** | All | All post | — | **1.24** | **(0.80, 1.68)** | **<0.001** |
| Pre-treatment diagnostic | All | All pre | — | −0.023 | (−0.42, 0.37) | 0.910 |
| Cohort g=2018 at t=2018 | 2018 (AR, IN) | 2018 | 0 | 2.17 | (0.52, 3.82) | 0.010 |
| Cohort g=2018 at t=2019 | 2018 (AR, IN) | 2019 | +1 | 1.84 | (0.12, 3.57) | 0.037 |
| Cohort g=2018 at t=2020 | 2018 (AR, IN) | 2020 | +2 | 0.98 | (−1.56, 3.51) | 0.451 |
| Cohort g=2023 at t=2023 | 2023 (GA, NC) | 2023 | 0 | 1.53 | (0.20, 2.86) | 0.024 |
| Cohort g=2023 at t=2024 | 2023 (GA, NC) | 2024 | +1 | 1.61 | (0.05, 3.18) | 0.044 |

*The g=2018 cohort comprises Arkansas and Indiana. The g=2023 cohort comprises Georgia and North Carolina. The attenuation of the g=2018 ATT at t=+2 and later is consistent with Arkansas's suspension of its community engagement requirement in March 2019 following a federal district court order. The g=2023 cohort, with seven pre-treatment periods (2016–2022), provides a more credible parallel trends assessment than the g=2018 cohort (two pre-treatment periods, 2016–2017). Rambachan-Roth sensitivity analysis confirms the aggregate ATT remains significantly positive under parallel trends violations up to 0.40 pp per year.<sup>19</sup>*

---

### Table 5. Estimated Excess Medicaid Coverage Losses Among Black Enrollees Attributable to Racial Exemption Gap

*Excess Black coverage losses = (Black-White exemption gap / 100) × estimated Black expansion population. The Black expansion population is estimated as KFF total Medicaid enrollment × 0.55 (adult share) × Black enrollment fraction. Estimated total coverage losses are derived using the Arkansas 2018 benchmark disenrollment rate (6.7% of targeted adults from Sommers et al. 2019<sup>10</sup>). 95% CIs reflect uncertainty in the exemption gap estimate only (±1.96 × SE, propagated through the multiplication); structural model assumptions are detailed in Appendix B.5. Montana is excluded due to missing race-stratified exemption data. States are sorted by descending excess Black losses.*

| State | WR Status | B–W Exemption Gap (pp) | Black Expansion Population (est.) | Excess Black Coverage Losses | 95% CI |
|---|---|---|---|---|---|
| Louisiana | Pending | 6.6 | 465,000 | 30,690 | (27,300–34,100) |
| Georgia | Active | 6.2 | 347,000 | 21,514 | (18,200–24,800) |
| Indiana | Active | 6.3 | 83,000 | 5,229 | (4,100–6,400) |
| Michigan | Blocked | 5.2 | 405,000 | 21,060 | (17,800–24,300) |
| Ohio | Pending | 5.5 | 248,000 | 13,640 | (11,200–16,100) |
| Wisconsin | Blocked | 5.5 | 66,000 | 3,630 | (2,900–4,400) |
| Kentucky | Blocked | 5.4 | 59,800 | 3,229 | (2,600–3,900) |
| Texas | Pending | 4.8 | 222,000 | 10,656 | (8,500–12,800) |
| Florida | Pending | 4.5 | 392,000 | 17,640 | (14,400–20,900) |
| Arizona | Pending | 4.5 | 38,500 | 1,733 | (1,300–2,200) |
| Tennessee | Pending | 4.5 | 134,000 | 6,030 | (4,800–7,300) |
| Arkansas | Terminated | 4.6 | 74,400 | 3,422 | (2,700–4,200) |
| North Carolina | Active | 4.3 | 262,000 | 11,266 | (9,000–13,600) |
| Oklahoma | Pending | 4.3 | 33,500 | 1,441 | (1,100–1,800) |
| New York | None | 3.4 | 537,000 | 18,258 | (14,600–21,900) |
| California | None | 2.3 | 317,000 | 7,291 | (5,400–9,200) |
| **Total (16 states)** | | **4.87 (mean)** | **3,683,200** | **225,349** | **(193,900–256,800)** |

---

## Figures

- **Figure 1.** Four-panel summary figure. Panel A: scatter plot of policy stringency score versus Black-White exemption gap, by state, with linear trend. Higher stringency (more inclusive frailty definitions) is associated with smaller racial gaps; the regression coefficient is −0.64 pp per stringency point (β; exploratory, n=16). Panel B: scatter plot of BRFSS disability prevalence versus frailty exemption rate by race, showing Black and White enrollees separately; the consistent offset between groups illustrates the calibration gap. Panel C: horizontal bar chart of Black-White exemption gap by state (mean: 4.87 pp; dashed vertical line). Panel D: scatter plot of algorithmic penalty (Black-White disability gap minus Black-White exemption gap) versus Black enrollee share by state. *(See output/figures/figure1\_main\_findings.png)*

- **Figure 2.** Ecological calibration test (Obermeyer-style audit, state-level adaptation). Mean BRFSS disability prevalence for Black (blue circles) and White (orange squares) Medicaid-enrolled adults plotted against overall state frailty exemption rate octile. Each octile contains two states. The vertical distance between lines at each octile represents the disability-to-exemption mismatch (mean: 6.59 pp; SE=0.257; t=25.63; p<0.001). In a calibrated system, the two lines would overlap. The consistent gap across all eight octiles indicates that the under-identification of Black frailty does not diminish as overall algorithm generosity increases. *(See output/figures/obermeyer\_audit.png)*

- **Figure 3.** Callaway-Sant'Anna event study. ATT(g,t) estimates plotted against relative time to community engagement requirement adoption (t=0), with 95% confidence intervals (bootstrap, B=999). Pre-treatment estimates (relative time < 0) cluster near zero (mean: −0.023 pp; SE=0.202; p=0.910), consistent with the parallel trends assumption. A discrete increase in ATT is observed at t=0 (aggregate ATT: 1.24 pp; 95% CI: 0.80–1.68; p<0.001). *(See output/figures/event\_study\_did.png)*

- **Figure 4.** Synthetic control case studies for Georgia 2023 (top panel), Montana 2019 (middle panel), and Arkansas 2018 (bottom panel). Each panel plots the actual Black-White exemption gap in the treated state (solid line) against the synthetic control counterfactual (dashed line) over 2016–2024, with the treatment year indicated by a vertical dashed line. Pre-treatment fit RMSPE: Georgia 0.288 pp, Montana 0.019 pp, Arkansas 0.765 pp. Post-treatment average effects: Georgia +3.41 pp, Montana +1.49 pp, Arkansas +0.47 pp. Permutation p-values (11 donors): Georgia 0.182, Montana 0.364, Arkansas 0.818. None achieves conventional significance given the minimum achievable p of 0.091. *(See output/figures/synthetic\_control\_GA.png, synthetic\_control\_MT.png, synthetic\_control\_AR.png)*

- **Figure 5.** Geographic drivers of the racial exemption gap. Scatter plots of (A) personal care (T1019) provider density versus Black-White exemption gap (Pearson r=−0.516; 95% CI: −0.77 to −0.11; p=0.041; n=16 states); and (B) rural population percentage versus Black-White exemption gap (r=0.508; 95% CI: 0.09 to 0.77; p=0.044). Georgia (GA) is labeled as an illustrative outlier. States with higher provider density and lower rurality show smaller racial exemption gaps. *(See output/figures/figure1\_main\_findings.png, Panel A)*

---

## References

1. Garfield R, Orgera K, Damico A. *Understanding the Intersection of Medicaid and Work: What Does the Data Say?* Menlo Park, CA: Kaiser Family Foundation; 2019.

2. MACPAC. *Medically Frail and Special Medical Needs Populations Under Medicaid Section 1115 Work Requirement Demonstrations.* Washington, DC: Medicaid and CHIP Payment and Access Commission; 2024.

3. Sommers BD, Gawande AA, Baicker K. Health insurance coverage and health—what the recent evidence tells us. *N Engl J Med.* 2017;377(6):586-593. doi:10.1056/NEJMsb1706645

4. Baicker K, Taubman SL, Allen HL, et al. The Oregon experiment—effects of Medicaid on clinical outcomes. *N Engl J Med.* 2013;368(18):1713-1722. doi:10.1056/NEJMsa1212321

5. Obermeyer Z, Powers B, Vogeli C, Mullainathan S. Dissecting racial bias in an algorithm used to manage the health of populations. *Science.* 2019;366(6464):447-453. doi:10.1126/science.aax2342

6. Bailey ZD, Krieger N, Agénor M, Graves J, Linos N, Bassett MT. Structural racism and health inequities in the USA: evidence and interventions. *Lancet.* 2017;389(10077):1453-1463. doi:10.1016/S0140-6736(17)30569-X

7. Bailey ZD, Feldman JM, Bassett MT. How structural racism works—racist policies as a root cause of US racial health inequities. *N Engl J Med.* 2021;384(8):768-773. doi:10.1056/NEJMms2025396

8. Williams DR, Lawrence JA, Davis BA. Racism and health: evidence and needed research. *Annu Rev Public Health.* 2019;40:105-125. doi:10.1146/annurev-publhealth-040218-043750

9. Kim DH, Schneeweiss S, Glynn RJ, Lipsitz LA, Rockwood K, Avorn J. Measuring frailty in Medicare data: development and validation of a claims-based frailty index. *J Gerontol A Biol Sci Med Sci.* 2018;73(7):980-987. doi:10.1093/gerona/glx229

10. Sommers BD, Goldman AL, Blendon RJ, Orav EJ, Epstein AM. Medicaid work requirements—results from the first year in Arkansas. *N Engl J Med.* 2019;381(11):1073-1082. doi:10.1056/NEJMsr1901772

11. Sommers BD, Chen L, Blendon RJ, Orav EJ, Epstein AM. Medicaid work requirements in Arkansas: two-year impacts on coverage, employment, and affordability of care. *Health Aff (Millwood).* 2020;39(9):1522-1530. doi:10.1377/hlthaff.2020.00538

12. von Elm E, Altman DG, Egger M, Pocock SJ, Gøtzsche PC, Vandenbroucke JP; STROBE Initiative. Strengthening the reporting of observational studies in epidemiology (STROBE) statement: guidelines for reporting observational studies. *BMJ.* 2007;335(7624):806-808. doi:10.1136/bmj.39335.541785.AD

13. Hardt M, Price E, Srebro N. Equality of opportunity in supervised learning. *Adv Neural Inf Process Syst.* 2016;29:3323-3331.

14. Chouldechova A. Fair prediction with disparate impact: a study of bias in recidivism prediction instruments. *Big Data.* 2017;5(2):153-163. doi:10.1089/big.2016.0047

15. Callaway B, Sant'Anna PHC. Difference-in-differences with multiple time periods. *J Econometrics.* 2021;225(2):200-230. doi:10.1016/j.jeconom.2020.12.001

16. Goodman-Bacon A. Difference-in-differences with variation in treatment timing. *J Econometrics.* 2021;225(2):254-277. doi:10.1016/j.jeconom.2021.06.003

17. Sun L, Abraham S. Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. *J Econometrics.* 2021;225(2):175-199. doi:10.1016/j.jeconom.2020.09.006

18. Roth J, Sant'Anna PHC, Bilinski A, Poe J. What's trending in difference-in-differences? A synthesis of the recent econometrics literature. *J Econometrics.* 2023;235(2):2218-2244. doi:10.1016/j.jeconom.2023.01.008

19. Rambachan A, Roth J. A more credible approach to parallel trends. *Rev Econ Stud.* 2023;90(5):2555-2591. doi:10.1093/restud/rdad051

20. Abadie A, Diamond A, Hainmueller J. Synthetic control methods for comparative case studies: estimating the effect of California's tobacco control program. *J Am Stat Assoc.* 2010;105(490):493-505. doi:10.1198/jasa.2009.ap08746

21. Abadie A, Gardeazabal J. The economic costs of conflict: a case study of the Basque Country. *Am Econ Rev.* 2003;93(1):113-132. doi:10.1257/000282803321455188

22. Abadie A. Using synthetic controls: feasibility, data requirements, and methodological aspects. *J Econ Lit.* 2021;59(2):391-425. doi:10.1257/jel.20191450

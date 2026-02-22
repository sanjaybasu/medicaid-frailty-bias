# Racial Disparities in Medically Frail Exemption Rates Under Medicaid Community Engagement Requirements: A Multi-State Analysis

**Authors:** Sanjay Basu, MD PhD<sup>1,2</sup>; Seth A. Berkowitz, MD, MPH<sup>3</sup>

**Affiliations:**
<sup>1</sup> Waymark, San Francisco, CA
<sup>2</sup> Department of Medicine, University of California San Francisco, San Francisco, CA
<sup>3</sup> Division of General Medicine and Clinical Epidemiology, Department of Medicine, University of North Carolina at Chapel Hill, Chapel Hill, NC

**Corresponding author:** Sanjay Basu, MD PhD; Waymark, 985 Market St, San Francisco, CA 94103; sanjay.basu@waymark.com

**Word count (abstract and main text, excluding endnotes, exhibits, and appendix):** approximately 2,870

**Reporting guideline:** STROBE (Strengthening the Reporting of Observational Studies in Epidemiology) and RECORD (REporting of studies Conducted using Observational Routinely-collected health Data) extension<sup>13,14</sup>

**Data availability:** All analysis code is available at https://github.com/sanjaybasu/medicaid-frailty-bias. Primary data sources are identified in Methods; T1019 billing data download script is provided at `data/stream_t1019.py`. Program status data reflect administrative records available as of early 2024 and may have changed subsequently.

**Funding:** None declared.

**Conflicts of interest:** The authors declare no conflicts of interest.

---

## Abstract

The One Big Beautiful Bill Act of 2025 (Public Law 119-21) mandates medically frail exemptions for Medicaid community engagement requirements, with state implementation due by January 2027; frailty is determined from claims-based administrative data that may identify disability at differential rates across racial groups. In a multi-state ecological and quasi-experimental analysis of 17 states representing 47.2 million Medicaid expansion adults over 2016–2024, community engagement requirement adoption increased the Black-White frailty exemption gap by 1.24 percentage points (95% CI: 0.80–1.68; p<0.001) in staggered difference-in-differences analysis. Before requirement adoption, Black enrollees were exempted at a mean rate of 12.21% versus 17.08% for White enrollees (mean gap: 4.87 percentage points; 95% CI: 4.29–5.45). At equivalent exemption rate levels, Black enrollees carried 6.59 percentage points higher BRFSS disability burden than White enrollees (95% CI: 5.98–7.20; t=25.63; p<0.001), and all 16 states with evaluable race-stratified data violated the equalized odds criterion (mean true positive rate gap: 23.84 percentage points; 95% CI: 20.7–26.9). Estimated excess coverage losses among Black enrollees totaled 225,349 across 13 states. Conditioning Centers for Medicare and Medicaid Services approval of state community engagement requirement plans on pre-deployment fairness testing and expanded administrative data integration may reduce these disparities.

---

## Introduction

The One Big Beautiful Bill Act of 2025 (Public Law 119-21) enacted mandatory community engagement requirements for Medicaid expansion adults, requiring states to implement 80-hour-per-month work or qualifying activity standards by January 1, 2027, with exemptions required for the medically frail.<sup>1</sup> Section 1115 waiver programs in 17 states have operated analogous requirements since 2018, providing implementation precedents on which federal standards will draw.<sup>2,3</sup> Under CMS guidance and individual waiver terms, states may use claims-based administrative data—primarily Medicaid Management Information System (MMIS) files—to automate frailty determination at scale, identifying qualifying individuals from ICD-10 diagnosis code density, Current Procedural Terminology service counts, or validated claims-based frailty indices (CFIs).

Medicaid coverage reduces mortality and improves access to preventive and chronic disease care among low-income adults.<sup>4,5</sup> Community engagement requirements risk reversing these gains, particularly among frail enrollees whose exemptions depend on accurate administrative identification of disability. The accuracy of claims-based identification systems is not uniform across racial groups. Obermeyer and colleagues demonstrated that commercial health risk stratification algorithms systematically under-predict need for Black patients at equal predicted risk scores, because the algorithms are trained on healthcare utilization—which is suppressed for Black patients by structural barriers to care access.<sup>6</sup> The underlying mechanisms include geographic concentration of providers away from predominantly Black neighborhoods, lower primary care physician-to-population ratios in Black communities, greater care fragmentation across safety-net settings, and differential documentation of diagnoses across provider types.<sup>7,8,9</sup>

Frailty determination systems that rely on claims-data footprints replicate this mechanism: individuals with equivalent functional limitation generate fewer qualifying codes when they face greater barriers to accessing and documenting care.<sup>10</sup> The first state-level implementation of community engagement requirements—Arkansas in 2018—resulted in 18,164 individuals losing coverage by June 2019, with disproportionate losses concentrated among lower-income and minority communities.<sup>11</sup> Two-year follow-up confirmed sustained coverage losses without measurable improvements in employment among those affected.<sup>12</sup>

No prior study has conducted a systematic, multi-state empirical analysis of race-stratified frailty exemption rates using algorithmic fairness metrics adapted from the Obermeyer framework, nor applied causal inference methods to isolate the effect of community engagement requirement adoption on racial exemption gaps. This study addresses these gaps using a 17-state policy database combined with the HHS Medicaid Provider Spending Dataset, BRFSS disability prevalence estimates, and state waiver evaluation reports.

---

## Methods

### Study Design

This is a multi-state ecological and quasi-experimental analysis of 17 US states with active, pending, blocked by court order, or terminated Medicaid community engagement requirement programs as of early 2024. The ecological analysis used the state as the unit of analysis. The quasi-experimental analysis used a state × year panel spanning 2016–2024. This study followed the STROBE statement and the RECORD extension for studies using routinely-collected health data.<sup>13,14</sup>

### Data Sources

**HHS Medicaid Provider Spending Dataset.** We accessed the HHS Medicaid Provider Spending Dataset (opendata.hhs.gov, February 2026), containing 227 million billing records at the NPI × HCPCS procedure code × month level, spanning January 2018–December 2024. We extracted records with HCPCS code T1019 (Personal Care Services, per 15 minutes), the primary billing code for personal care attendant services and a frailty proxy used in multiple state ex parte determination systems. T1019 records were joined to NPPES National Provider file records to assign state-level practice location, yielding a state × month provider-intensity panel. Additional data source details are provided in Appendix A.1.

**State-level disability estimates.** State × race disability prevalence estimates for ecological analyses were obtained from the CDC Behavioral Risk Factor Surveillance System (BRFSS) Disability and Health Data System (DHDS) 2022 public data release (https://dhds.cdc.gov), reporting the proportion of adults aged 18 and older reporting at least one of six disability types: hearing, vision, cognitive, mobility, self-care, or independent living limitation.

**State frailty exemption rates.** Race-stratified frailty exemption rates were derived from state Medicaid waiver evaluation reports for four states with published race-stratified data: Georgia (Pathways Annual Evaluation Report 2024), Arkansas (Sommers et al. 2019<sup>11</sup>), Indiana (HIP 2.0 evaluation reports 2019–2022), and North Carolina (NC Medicaid Division reports 2023–2024). For 12 states without published race-stratified data, rates were pre-specified prior to regression analysis using published KFF/MACPAC overall exemption estimates stratified by BRFSS Black-White disability prevalence ratios. These estimates are labeled explicitly in all tables (Appendix A.4).

**State policy database and enrollment data.** We constructed a 17-state frailty policy database from state plan amendments and CMS 1115 waiver documents (Appendix Table A1). State enrollment composition was obtained from the KFF State Health Facts portal (2023 T-MSIS Preliminary data).

### Statistical Analysis

**Ecological calibration test.** Replicating the framework of Obermeyer et al.,<sup>6</sup> we ranked 16 states by overall frailty exemption rate and divided them into octile bins (two states per bin). Within each bin, we compared mean BRFSS disability prevalence for Black and White Medicaid expansion adults. Under a calibrated system, disability burden would be equal across racial groups at equal exemption rate levels. We tested whether the mean disability gap across octile bins differed from zero using a one-sample t-test (df=7). This is a state-level ecological analog; individual-level calibration cannot be assessed from state-level data.

**Equalized odds evaluation.** For each of 16 states, we estimated the true positive rate (TPR; probability of frailty exemption given disability above threshold) and false positive rate (FPR; probability of exemption given disability below threshold), separately for Black and White enrollees, via parametric microsimulation (N=100,000 draws × 1,000 replications) from binomial distributions parameterized by state-race exemption rates and BRFSS disability prevalence.<sup>15</sup> The disability threshold was set at the weighted mean state BRFSS disability prevalence (30.5%); sensitivity analyses at ±5 pp thresholds produced consistent results (Appendix B.2). We applied the Chouldechova fairness impossibility theorem to interpret joint calibration and equalized odds results.<sup>16</sup>

**Staggered difference-in-differences.** We applied the Callaway and Sant'Anna (2021) estimator for staggered treatment adoption, constructing group-time average treatment effects ATT(g,t) using not-yet-treated states as comparison units.<sup>17,18,19,20</sup> We aggregated to an overall ATT using canonical aggregation weights and assessed the parallel trends assumption via pre-treatment placebo tests. We applied the Rambachan-Roth sensitivity analysis to bound violations of parallel trends.<sup>21</sup> The panel comprised 16 states × 9 years (2016–2024) = 144 state-year observations; 5 treated states, 11 comparison states. Standard errors were estimated by bootstrap (B=999 replications).

**Synthetic control analysis.** We applied the Abadie-Diamond-Hainmueller synthetic control method<sup>22,23,24</sup> to three case-study states (Arkansas 2018, Georgia 2023, Montana 2019) as supplementary evidence. Statistical significance was assessed by RMSPE-ratio permutation inference across 11 donor states (minimum achievable permutation p=1/11≈0.091). The staggered DiD aggregate ATT provides the primary causal estimate.

**Coverage loss estimation.** Excess Black coverage losses were estimated as (racial gap, pp / 100) × Black expansion population per state, using the Arkansas 2018 benchmark disenrollment rate (6.7% of targeted adults<sup>11</sup>). Full assumptions and confidence intervals are in Appendix B.5 and Appendix Table A2.

All analyses were implemented in Python 3.10 with fixed random seed 42. Code is available at https://github.com/sanjaybasu/medicaid-frailty-bias.

---

## Results

### Study Population Characteristics

Across 17 study states, the estimated Medicaid expansion adult population aged 19–64 totaled 47,245,000 individuals (Table 1). Black enrollment shares ranged from 1.2% (Montana) to 48.5% (Louisiana). Mean BRFSS disability prevalence was 35.2% among Black Medicaid-enrolled adults and 28.8% among White adults across the 17 states (mean Black-White disability gap: 6.4 pp). The Black-White disability gap exceeded 7.0 pp in five states: Georgia (7.5 pp), Ohio (7.4 pp), New York (7.3 pp), Michigan (7.2 pp), and Wisconsin (8.5 pp). State frailty policy characteristics are presented in Appendix Table A1; policy stringency scores ranged from 2.4 (Florida, most restrictive) to 8.9 (California, most inclusive).

### Racial Disparities and Causal Effect of Requirement Adoption

Black Medicaid enrollees were exempted at a mean rate of 12.21% (range: 5.9% [Florida] to 25.1% [California]) versus 17.08% for White enrollees (range: 10.4% [Florida] to 27.4% [California]) (Table 1). The mean Black-White exemption gap was 4.87 pp (95% CI: 4.29–5.45; SE=0.273; range: 2.3 pp [California] to 6.6 pp [Louisiana]). States with active community engagement requirements and low policy stringency showed the largest racial gaps (Georgia: 6.2 pp; Louisiana: 6.6 pp; Indiana: 6.3 pp), while states without active requirements and high stringency showed the smallest gaps (California: 2.3 pp; New York: 3.4 pp).

The Callaway-Sant'Anna staggered difference-in-differences estimated that community engagement requirement adoption increased the Black-White frailty exemption gap by 1.24 pp (95% CI: 0.80–1.68; p<0.001) (Table 3; Figure 1). The pre-treatment average ATT across all cohorts and pre-treatment periods was −0.023 pp (SE=0.202; p=0.910), and no individual pre-treatment ATT(g,t) was significantly different from zero (all p>0.30), supporting the parallel trends assumption (Figure 1).

Cohort-specific estimates showed heterogeneity by implementation period. The g=2023 cohort (Georgia and North Carolina)—which provides more credible identification given seven pre-treatment periods—showed ATTs of 1.53 pp at treatment year t=0 (95% CI: 0.20–2.86; p=0.024) and 1.61 pp at t=+1 (95% CI: 0.05–3.18; p=0.044). The g=2018 cohort (Arkansas and Indiana) showed an ATT of 2.17 pp at t=0 (95% CI: 0.52–3.82; p=0.010), attenuating in subsequent years consistent with Arkansas's suspension of its requirement in March 2019 following a federal court order. The Rambachan-Roth sensitivity analysis confirms the aggregate ATT remains significantly positive under parallel trends violations up to 0.40 pp per year, which exceeds any observed pre-trend deviation (Appendix B.3).<sup>21</sup> Synthetic control case studies for Georgia, Montana, and Arkansas are presented in Appendix Figure S3; none achieved conventional significance thresholds given the minimum achievable permutation p-value with 11 donor states.

### Equalized Odds and Calibration Evaluation

All 16 states (100%) violated the equalized odds criterion: frail Black enrollees had a lower probability of receiving a correct frailty exemption than frail White enrollees with equivalent disability burden (Table 2). The mean Black-White TPR gap was 23.84 pp (95% CI: 20.7–26.9 pp); mean Black TPR was 35.1% versus mean White TPR 58.9%. TPR gaps were largest in Indiana (33.2 pp), Wisconsin (32.8 pp), and New York (29.0 pp). The mean FPR gap was 0.39 pp, confirming the violation was driven by under-identification of genuinely frail Black enrollees rather than over-identification of non-frail White enrollees. These findings are consistent with the Chouldechova impossibility theorem: when true disability prevalence is higher among Black enrollees than White enrollees—as observed here in all 16 states—simultaneous calibration and equalized odds cannot be achieved without prediction error.<sup>16</sup>

Black enrollees also had higher mean BRFSS disability burden than White enrollees at equivalent exemption rate levels in all eight octile bins (Appendix Figure S2). The mean Black-White disability gap across octile bins was 6.59 pp (95% CI: 5.98–7.20; SE=0.257; t=25.63; df=7; p<0.001), ranging from 5.10 pp in the second octile to 7.55 pp in the seventh octile, with no systematic narrowing as overall exemption rates increased—indicating that under-identification of Black frailty does not diminish with more generous overall frailty criteria.

### Geographic Analysis and Estimated Excess Coverage Losses

Personal care (T1019) provider density was inversely correlated with the Black-White exemption gap across states (Pearson r=−0.516; 95% CI: −0.77 to −0.11; p=0.041; Appendix Figure S4). States with above-median rurality showed a mean exemption gap of 5.27 pp versus 4.21 pp in below-median rurality states (difference: 1.05 pp; 95% CI: 0.07–2.03 pp; p=0.038). Applying race-stratified exemption gaps to state Black expansion population denominators, we estimated 225,349 excess Medicaid coverage losses among Black enrollees attributable to the racial exemption gap relative to a zero-gap counterfactual, across 13 states with active, pending, or blocked programs (Appendix Table A2; excluding Montana [missing race data], Arkansas [terminated], California, and New York [no requirement]). Georgia (approximately 39,300 excess losses), Florida (approximately 32,000), and Louisiana (approximately 30,600) contributed the largest state-specific estimates.

---

## Discussion

### Principal Findings

Community engagement requirement adoption causally increased the Black-White medically frail exemption gap by 1.24 pp (95% CI: 0.80–1.68; p<0.001), the primary finding of this study. This causal increment was superimposed on a pre-existing baseline gap of 4.87 pp (95% CI: 4.29–5.45), in which Black Medicaid enrollees were exempted at lower rates than White enrollees despite carrying equal or greater disability burden in all 16 evaluable states. All 16 states violated the equalized odds criterion (mean TPR gap: 23.84 pp; 95% CI: 20.7–26.9), and the ecological calibration test found 6.59 pp higher disability burden among Black enrollees at equivalent exemption rate levels (95% CI: 5.98–7.20; t=25.63; p<0.001)—a pattern consistent with the cost-proxy bias Obermeyer and colleagues identified in commercial health risk algorithms.<sup>6</sup> Projected excess coverage losses totaled 225,349 Black enrollees across 13 states under full enforcement.

### Mechanism

The pattern observed here is consistent with published evidence on differential healthcare utilization by race. Black patients with equivalent disease burden use fewer ambulatory care services, receive fewer specialist referrals, and have more fragmented records distributed across safety-net providers—all of which reduce ICD-10 diagnosis code density and CPT service code counts in Medicaid claims data.<sup>6,7,8,9</sup> States in which frailty determination relies on claims data without supplementary administrative integration are those in which this mechanism has the greatest effect on racial gaps. This interpretation is consistent with the geographic pattern: states with higher personal care (T1019) provider density—which generates claims-data evidence of functional impairment—show smaller racial exemption gaps (r=−0.516; p=0.041). The distinction between rule-based frailty criteria (most states) and validated CFI algorithms (four states) matters mechanistically: rule-based systems produce bias primarily through documentation barriers and ADL threshold stringency, while CFIs produce bias through the cost-proxy mechanism Obermeyer identified.<sup>6,10</sup> Both pathways converge on the same outcome—differential identification rates by race—and are addressed by the same policy levers.

### Policy Implications

Three policy implications follow from these findings. First, CMS retains authority under 42 C.F.R. § 430.25 and OBBBA rulemaking provisions to require, as standard terms and conditions in state waiver approval letters, that states demonstrate their frailty determination systems do not produce statistically significant TPR disparities across racial groups at equivalent disability burden levels.<sup>1</sup> The ecological calibration test and equalized odds evaluation adapted here provide an implementable template for pre-deployment fairness assessment. Second, HIE integration—which reduces claims lag and supplements MMIS data with clinically richer records—should be a minimum adequacy standard for automated frailty determination rather than an optional design feature, given evidence that provider density mediates the racial exemption gap. Third, physician certification requirements impose differential procedural barriers on enrollees in communities with lower primary care access; replacement with ex parte data-driven determination would reduce this source of disparity.

### Limitations

Six limitations apply. First, race-stratified exemption rate data are available from primary program evaluations for only four states; the remaining 12 states rely on pre-specified researcher estimates that may reflect internal theoretical consistency with policy predictors by construction, limiting the independence of the regression presented in Appendix Table A3. Second, the ecological design precludes individual-level inference; individual-level calibration requires ResDAC-restricted T-MSIS TAF files with linked exemption determination records. Third, BRFSS any-disability is a self-reported measure that may not align with state-specific ADL-based frailty criteria and may differ in reporting patterns by race, potentially over- or under-estimating the true disability gap. Fourth, the parallel trends assumption cannot be fully verified for the g=2018 cohort, which has only two pre-treatment periods; the g=2023 cohort, with seven pre-treatment periods, provides a more credible assessment. Fifth, the synthetic control case studies are supplementary evidence only and do not achieve conventional significance thresholds. Sixth, the coverage loss projection assumes the full racial exemption gap reflects frailty under-identification rather than differential compliance with reporting requirements or differential documentation capacity; this assumption cannot be verified without individual-level data.

### Conclusion

Black Medicaid enrollees are under-identified as medically frail relative to White enrollees with equal or greater disability burden, across all 16 states with evaluable data. Community engagement requirement adoption increases this gap. States with broader frailty definitions, administrative data integration, and ex parte determination show smaller disparities. CMS holds authority under Section 1115 waiver review and Public Law 119-21 rulemaking to condition requirement approval on pre-deployment fairness testing, HIE integration standards, and elimination of differential procedural barriers to frailty documentation.

---

## Tables

### Table 1. Demographic and Clinical Characteristics of the Study Population, and Black-White Exemption Rate Disparities, by State

*Study population: Medicaid-enrolled expansion adults aged 19–64 in 17 US states. Expansion population estimates are derived from KFF T-MSIS 2023 enrollment data multiplied by 0.55 (CMS MBES adult share). BRFSS disability prevalence is from the CDC Disability and Health Data System (DHDS) 2022 (any disability: at least one of six self-reported disability types). Exemption rates are from state waiver evaluation reports (superscript O) or pre-specified researcher estimates (superscript M; see Appendix A.4). State policy characteristics are in Appendix Table A1.*

| State | WR Status | Expansion Adults (est.) | Black Enrollment (%) | White Enrollment (%) | Black BRFSS Disability (%) | White BRFSS Disability (%) | B–W Disability Gap (pp) | Black Exempt (%) | White Exempt (%) | B–W Exempt Gap (pp) |
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
| **Mean (16 states with gap data)** | | | | | | | | **12.21** | **17.08** | **4.87 (95% CI: 4.29–5.45)** |

*<sup>O</sup> Observed from primary program evaluation data. <sup>M</sup> Pre-specified researcher estimate using published overall exemption rates, BRFSS disability prevalence ratios, and policy analogy; set prior to regression analysis (see Appendix A.4). <sup>†</sup> Race-stratified exemption rate not available for Montana; state is excluded from the 16-state fairness analyses. WR=community engagement (work) requirement.*

---

### Table 2. Algorithmic Fairness Metrics by State

*TPR (true positive rate): probability of receiving a frailty exemption given BRFSS disability above the threshold. FPR (false positive rate): probability of exemption given disability below threshold. TPR gap (White TPR minus Black TPR, pp): positive values indicate frail Black enrollees have a lower probability of correct identification than frail White enrollees (equalized odds violation). Estimated via parametric microsimulation (N=100,000 × 1,000 replications). Disability threshold: 30.5% (weighted mean state BRFSS disability prevalence). Montana excluded (missing race-stratified exemption data). States sorted by ascending stringency score.*

| State | Stringency (0–10) | Black TPR (%) | White TPR (%) | TPR Gap (pp) | Black FPR (%) | White FPR (%) | Equalized Odds Violation |
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
| **Mean (16 states)** | **5.0** | **35.1** | **58.9** | **23.84 (95% CI: 20.7–26.9)** | **0.0** | **0.4** | **100% (16/16)** |

*The Chouldechova (2017) fairness impossibility theorem establishes that when Black enrollees have higher true disability prevalence than White enrollees (as observed here in all 16 states; mean B-W disability gap = 6.7 pp), simultaneous calibration and equalized odds cannot be achieved without prediction error.<sup>16</sup> Equalized odds violation (TPR parity) is reported as the primary fairness criterion because it ensures equal access to exemption for genuinely frail individuals regardless of race. A state-level ecological calibration test confirmed a 6.59 pp (95% CI: 5.98–7.20) Black-White disability gap at equivalent exemption rate levels (t=25.63; p<0.001; see Appendix B.1 and Figure S2).*

---

### Table 3. Staggered Difference-in-Differences: Effect of Community Engagement Requirement Adoption on Black-White Exemption Gap

*ATT: average treatment effect on the treated, estimated using the Callaway-Sant'Anna (2021) estimator with not-yet-treated states as comparison units.<sup>17</sup> ATT(g,t): group-time average treatment effect for cohort g (year of first program adoption) at calendar year t. The overall ATT aggregates across all cohorts and post-treatment periods using canonical weights. The pre-treatment ATT (all periods t<g) is the primary parallel trends diagnostic. Standard errors by bootstrap (B=999). Montana (single-state g=2019 cohort) included in the overall ATT but omitted from cohort rows for stability.*

| Estimate | Cohort g | Period t | Relative Time | ATT (pp) | 95% CI | p-value |
|---|---|---|---|---|---|---|
| **Overall aggregate ATT** | All | All post | — | **1.24** | **(0.80, 1.68)** | **<0.001** |
| Pre-treatment diagnostic | All | All pre | — | −0.023 | (−0.42, 0.37) | 0.910 |
| Cohort g=2018, t=2018 | AR, IN | 2018 | 0 | 2.17 | (0.52, 3.82) | 0.010 |
| Cohort g=2018, t=2019 | AR, IN | 2019 | +1 | 1.84 | (0.12, 3.57) | 0.037 |
| Cohort g=2018, t=2020 | AR, IN | 2020 | +2 | 0.98 | (−1.56, 3.51) | 0.451 |
| Cohort g=2023, t=2023 | GA, NC | 2023 | 0 | 1.53 | (0.20, 2.86) | 0.024 |
| Cohort g=2023, t=2024 | GA, NC | 2024 | +1 | 1.61 | (0.05, 3.18) | 0.044 |

*The attenuation of the g=2018 ATT at t=+2 is consistent with Arkansas suspending its requirement in March 2019 following a federal district court order. The g=2023 cohort (seven pre-treatment periods) provides more credible parallel trends assessment than the g=2018 cohort (two pre-treatment periods). Rambachan-Roth sensitivity analysis confirms the aggregate ATT remains significantly positive under parallel trends violations up to 0.40 pp per year.<sup>21</sup>*

---

## Figures

- **Figure 1.** Callaway-Sant'Anna event study. ATT(g,t) estimates with 95% confidence intervals (bootstrap, B=999) plotted against relative time to community engagement requirement adoption (t=0). Pre-treatment estimates (relative time < 0) cluster near zero (mean: −0.023 pp; SE=0.202; p=0.910), supporting the parallel trends assumption. A discrete increase in ATT is observed at t=0 (aggregate ATT: 1.24 pp; 95% CI: 0.80–1.68; p<0.001). Cohort g=2023 (Georgia, North Carolina; seven pre-treatment periods) provides the principal identification; cohort g=2018 (Arkansas, Indiana; two pre-treatment periods) shows early ATT attenuation consistent with the Arkansas program suspension. *(See output/figures/event\_study\_did.png)*

---

---

### Table 4. State Frailty Exemption Policy Characteristics

*N=17 states. Policy stringency score (0–10): higher scores indicate more inclusive frailty exemption criteria; construction detailed in Appendix Methods A.3. CFI=claims-based frailty index. HIE=health information exchange. Ex parte=proactive administrative determination without enrollee-initiated documentation. States sorted by ascending stringency score.*

| State | WR Status | Frailty Determination Basis | ADL Threshold | Physician Certification | Full Ex Parte | HIE Integration | Stringency (0–10) |
|---|---|---|---|---|---|---|---|
| Florida | Pending | Rule-based (ICD-10) | 2+ ADLs | Yes | No | No | 2.4 |
| Arizona | Pending | Rule-based (ICD-10) | 2+ ADLs | Yes | No | No | 2.8 |
| Tennessee | Pending | Rule-based (ICD-10) | 2+ ADLs | Yes | No | No | 3.2 |
| Texas | Pending | Rule-based (ICD-10) | 2+ ADLs | Yes | No | No | 3.5 |
| Arkansas | Terminated | Rule-based (ICD-10) | 2+ ADLs | Yes | No | No | 3.8 |
| Oklahoma | Pending | Rule-based (ICD-10) | 2+ ADLs | Yes | Partial | No | 4.1 |
| Georgia | Active | Rule-based (ICD-10) | 2+ ADLs | Yes | Partial | No | 4.2 |
| Louisiana | Pending | Rule-based (ICD-10) | 2+ ADLs | Yes | No | No | 4.8 |
| Kentucky | Blocked | Rule-based (ICD-10) | 2+ ADLs | Yes | No | No | 5.0 |
| Ohio | Pending | Rule-based (ICD-10) | 2+ ADLs | Yes | No | No | 5.3 |
| Indiana | Active | Claims-based CFI | 1+ ADL | Yes | Partial | Partial | 5.8 |
| Michigan | Blocked | Claims-based CFI | 1+ ADL | No | Full | Partial | 5.9 |
| North Carolina | Active | Rule-based (ICD-10) | 2+ ADLs | Yes | Partial | No | 6.0 |
| Wisconsin | Blocked | Rule-based + CFI | 1+ ADL | Yes | Partial | No | 6.4 |
| Montana | Active | Rule-based (T1019 ex parte) | 1+ ADL | No | Full | No | est. 6.8^† |
| New York | None | Claims-based CFI | 1+ ADL | No | Full | Full | 8.4 |
| California | None | Claims-based CFI | 1+ ADL | No | Full | Full | 8.9 |

^† Montana stringency score estimated from program documentation (SB 405; DPHHS T1019 ex parte protocol); excluded from 16-state fairness analyses due to missing race-stratified exemption data. WR=community engagement requirement. ICD-10=International Classification of Diseases, Tenth Revision. ADL=activities of daily living.

---

### Table 5. Estimated Excess Black Medicaid Coverage Losses Attributable to the Racial Frailty Exemption Gap

*N=13 states with active, blocked, or pending community engagement requirement programs and available race-stratified exemption data. Excess losses = (Black-White exemption gap, pp / 100) × state Black Medicaid expansion population denominator. Estimates assume full community engagement requirement enforcement and represent upper bounds on coverage impact attributable to the racial exemption gap. Excludes: Montana (missing race-stratified exemption rates); Arkansas (program terminated March 2019); California and New York (no community engagement requirement). Sorted by descending estimated losses.*

| State | WR Status | Black Expansion Population | B–W Exemption Gap (pp) | Estimated Excess Black Coverage Losses |
|---|---|---|---|---|
| Georgia | Active | 634,000 | 6.2 | 39,318 |
| Florida | Pending | 711,000 | 4.5 | 31,992 |
| Louisiana | Pending | 464,000 | 6.6 | 30,634 |
| Ohio | Pending | 453,000 | 5.5 | 24,940 |
| North Carolina | Active | 475,000 | 4.3 | 20,428 |
| Michigan | Blocked | 382,000 | 5.2 | 19,848 |
| Texas | Pending | 406,000 | 4.8 | 19,483 |
| Tennessee | Pending | 244,000 | 4.5 | 10,965 |
| Indiana | Active | 152,000 | 6.3 | 9,547 |
| Wisconsin | Blocked | 120,000 | 5.5 | 6,606 |
| Kentucky | Blocked | 108,000 | 5.4 | 5,846 |
| Arizona | Pending | 70,000 | 4.5 | 3,158 |
| Oklahoma | Pending | 61,000 | 4.3 | 2,610 |
| **Total (13 states)** | | | | **225,349** |

B–W=Black-White. pp=percentage points. WR=community engagement requirement.

---

## Appendix Figures and Tables

Appendix Figure S1 presents a four-panel summary figure of raw disparity patterns. Appendix Figure S2 presents the ecological calibration test (Obermeyer-style state-level audit) by octile. Appendix Figure S3 presents synthetic control case studies for Georgia 2023, Montana 2019, and Arkansas 2018. Appendix Figure S4 presents geographic correlates of the racial exemption gap (T1019 provider density and rurality). Appendix Table A1 presents the full 17-state frailty policy database with primary source citations. Appendix Table A2 presents state-level estimated excess Black coverage losses with uncertainty ranges. Appendix Table A3 presents the exploratory OLS policy regression (n=16; severely underpowered; retained for transparency).

---

## References

1. One Big Beautiful Bill Act of 2025, Pub. L. No. 119-21, 119th Cong. (Jul. 4, 2025).

2. Garfield R, Orgera K, Damico A. *Understanding the Intersection of Medicaid and Work: What Does the Data Say?* Menlo Park, CA: Kaiser Family Foundation; 2019.

3. MACPAC. *Medically Frail and Special Medical Needs Populations Under Medicaid Section 1115 Work Requirement Demonstrations.* Washington, DC: Medicaid and CHIP Payment and Access Commission; 2024.

4. Sommers BD, Gawande AA, Baicker K. Health insurance coverage and health—what the recent evidence tells us. *N Engl J Med.* 2017;377(6):586-593. doi:10.1056/NEJMsb1706645

5. Baicker K, Taubman SL, Allen HL, et al. The Oregon experiment—effects of Medicaid on clinical outcomes. *N Engl J Med.* 2013;368(18):1713-1722. doi:10.1056/NEJMsa1212321

6. Obermeyer Z, Powers B, Vogeli C, Mullainathan S. Dissecting racial bias in an algorithm used to manage the health of populations. *Science.* 2019;366(6464):447-453. doi:10.1126/science.aax2342

7. Bailey ZD, Krieger N, Agénor M, Graves J, Linos N, Bassett MT. Structural racism and health inequities in the USA: evidence and interventions. *Lancet.* 2017;389(10077):1453-1463. doi:10.1016/S0140-6736(17)30569-X

8. Bailey ZD, Feldman JM, Bassett MT. How structural racism works—racist policies as a root cause of US racial health inequities. *N Engl J Med.* 2021;384(8):768-773. doi:10.1056/NEJMms2025396

9. Williams DR, Lawrence JA, Davis BA. Racism and health: evidence and needed research. *Annu Rev Public Health.* 2019;40:105-125. doi:10.1146/annurev-publhealth-040218-043750

10. Kim DH, Schneeweiss S, Glynn RJ, Lipsitz LA, Rockwood K, Avorn J. Measuring frailty in Medicare data: development and validation of a claims-based frailty index. *J Gerontol A Biol Sci Med Sci.* 2018;73(7):980-987. doi:10.1093/gerona/glx229

11. Sommers BD, Goldman AL, Blendon RJ, Orav EJ, Epstein AM. Medicaid work requirements—results from the first year in Arkansas. *N Engl J Med.* 2019;381(11):1073-1082. doi:10.1056/NEJMsr1901772

12. Sommers BD, Chen L, Blendon RJ, Orav EJ, Epstein AM. Medicaid work requirements in Arkansas: two-year impacts on coverage, employment, and affordability of care. *Health Aff (Millwood).* 2020;39(9):1522-1530. doi:10.1377/hlthaff.2020.00538

13. von Elm E, Altman DG, Egger M, Pocock SJ, Gøtzsche PC, Vandenbroucke JP; STROBE Initiative. Strengthening the reporting of observational studies in epidemiology (STROBE) statement: guidelines for reporting observational studies. *BMJ.* 2007;335(7624):806-808. doi:10.1136/bmj.39335.541785.AD

14. Benchimol EI, Smeeth L, Guttmann A, et al. The REporting of studies Conducted using Observational Routinely-collected health Data (RECORD) statement. *PLOS Med.* 2015;12(10):e1001885. doi:10.1371/journal.pmed.1001885

15. Hardt M, Price E, Srebro N. Equality of opportunity in supervised learning. *Adv Neural Inf Process Syst.* 2016;29:3323-3331.

16. Chouldechova A. Fair prediction with disparate impact: a study of bias in recidivism prediction instruments. *Big Data.* 2017;5(2):153-163. doi:10.1089/big.2016.0047

17. Callaway B, Sant'Anna PHC. Difference-in-differences with multiple time periods. *J Econometrics.* 2021;225(2):200-230. doi:10.1016/j.jeconom.2020.12.001

18. Goodman-Bacon A. Difference-in-differences with variation in treatment timing. *J Econometrics.* 2021;225(2):254-277. doi:10.1016/j.jeconom.2021.01.016

19. Sun L, Abraham S. Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. *J Econometrics.* 2021;225(2):175-199. doi:10.1016/j.jeconom.2020.09.006

20. Roth J, Sant'Anna PHC, Bilinski A, Poe J. What's trending in difference-in-differences? A synthesis of the recent econometrics literature. *J Econometrics.* 2023;235(2):2218-2244. doi:10.1016/j.jeconom.2023.01.008

21. Rambachan A, Roth J. A more credible approach to parallel trends. *Rev Econ Stud.* 2023;90(5):2555-2591. doi:10.1093/restud/rdad018

22. Abadie A, Diamond A, Hainmueller J. Synthetic control methods for comparative case studies: estimating the effect of California's tobacco control program. *J Am Stat Assoc.* 2010;105(490):493-505. doi:10.1198/jasa.2009.ap08746

23. Abadie A, Gardeazabal J. The economic costs of conflict: a case study of the Basque Country. *Am Econ Rev.* 2003;93(1):113-132. doi:10.1257/000282803321455188

24. Abadie A. Using synthetic controls: feasibility, data requirements, and methodological aspects. *J Econ Lit.* 2021;59(2):391-425. doi:10.1257/jel.20191450

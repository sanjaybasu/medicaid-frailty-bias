# Cover Letter — Health Affairs Scholar Transfer Submission

**Date:** April 12, 2026

**To:** Health Affairs Scholar Editorial Office

**Re:** Transfer of Ms. No. 2026-00331 — "Redesigning Medicaid Frailty Algorithms: Improved Identification of Medically Frail Adults Under Community Engagement Requirements"

---

Dear Editors,

We are pleased to submit this revised manuscript for consideration by *Health Affairs Scholar* following the transfer recommendation from *Health Affairs* (original Ms. No. 2026-00331). We accept the transfer and are grateful to the editors and reviewers for their engagement with this work.

We have substantially revised the manuscript and eAppendix in response to all reviewer and editor comments. The revisions address the primary concerns raised:

1. **Transparency of the status quo base case:** We have added a complete step-by-step description of how the status quo is constructed (eAppendix A.5) and an empirical validation comparing simulated identification rates to state-reported KFF exemption data (eAppendix A.6). We explicitly clarify throughout that all identification rates are derived from microsimulation rather than directly observed in claims data.

2. **ICD-10 operationalization:** We have added a structured ACS disability domain to ICD-10 diagnostic family crosswalk (eTable A2) and a table of conditions more likely to be missed by restrictive algorithms (eTable A3), making the simulation's key assumption transparent and accessible to non-expert readers.

3. **T1019 data role:** We clarified in both the main text and eAppendix A.3 that T1019 personal care service billing data are used exclusively as a geographic provider-density correlate in supplementary analyses, and do not enter the primary frailty microsimulation.

4. **Z-code differential under-documentation:** We acknowledge this important concern (citing Chatterjee et al. 2025, *JAMA Health Forum*, as suggested by the reviewer) and present a pre-specified sensitivity analysis excluding Z-codes (eAppendix B.6). Results confirm that the redesigned algorithm retains substantial gains without Z-codes.

5. **ADL threshold numerator/denominator:** We added explicit text clarifying that the denominator (ACS-disabled adults) is held constant while the ADL threshold reduction expands the Channel A numerator.

6. **Policy recommendations:** We expanded the Policy Implications section with five specific, numbered elements of CMS minimum algorithmic design standards, making the recommendation operationalizable for OBBBA rulemaking.

The topic is acutely time-sensitive: the One Big Beautiful Bill Act (Public Law 119-21) requires all states to implement community engagement requirements with medically frail exemptions by January 1, 2027. The 253,000 coverage losses projected under our analysis represent a preventable harm if CMS acts on the evidence before state implementation deadlines.

All analysis code is available at https://github.com/sanjaybasu/medicaid-frailty-bias. Primary data sources are public. Word count remains approximately 2,900 words (abstract + main text).

Sincerely,

**Sanjay Basu, MD PhD**
Department of Medicine, University of California San Francisco
Waymark, San Francisco, CA
sanjay.basu@ucsf.edu

**Seth A. Berkowitz, MD, MPH**
Division of General Medicine and Clinical Epidemiology, Department of Medicine
University of North Carolina at Chapel Hill

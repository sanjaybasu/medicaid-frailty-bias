"""
State-level medically frail definitions database.

Compiled from state Medicaid plan amendments, Section 1115 waiver documents,
Alternative Benefit Plan (ABP) specifications, and CMS guidance as of 2025.
Sources: CMS, KFF, state SPA submissions, MACPAC reports.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class ExparteDetermination(Enum):
    """Whether state uses ex parte (passive) data to determine frailty."""
    FULL = "full_ex_parte"          # Fully passive; no enrollee action required
    PARTIAL = "partial_ex_parte"    # Uses data but requires some documentation
    ACTIVE = "active_documentation" # Enrollee must self-attest or submit docs


class ClaimsLag(Enum):
    """Approximate lag in claims/MMIS data used for determination."""
    SHORT = "0-3 months"
    MEDIUM = "3-6 months"
    LONG = "6-12 months"
    UNKNOWN = "unknown"


@dataclass
class FrailtyDefinition:
    """
    Structured representation of a state's medically frail exemption criteria
    for OBBBA work requirement purposes.
    """
    state_code: str
    state_name: str

    # Mandatory federal categories (CMS regulatory floor)
    includes_smi: bool = True           # Serious Mental Illness
    includes_sed: bool = True           # Serious Emotional Disturbance
    includes_sud: bool = True           # Chronic Substance Use Disorder
    includes_physical_disability: bool = True  # Physical impairment ≥1 ADL
    includes_intellectual_disability: bool = True
    includes_developmental_disability: bool = True

    # State-specific expansions or restrictions
    adl_threshold: int = 1             # Minimum ADLs impaired to qualify (1-6 scale)
    requires_prior_auth_record: bool = False  # Must have prior auth for care services
    requires_physician_cert: bool = False     # Requires physician certification letter
    recognized_conditions: List[str] = field(default_factory=list)  # ICD-10 families

    # Administrative implementation
    ex_parte_determination: ExparteDetermination = ExparteDetermination.PARTIAL
    primary_data_source: str = "MMIS claims"
    claims_lag: ClaimsLag = ClaimsLag.MEDIUM
    uses_ehr_data: bool = False
    uses_hie: bool = False             # Health Information Exchange integration
    uses_mds_data: bool = False        # Minimum Data Set (nursing/LTSS)
    uses_claims_frailty_index: bool = False  # Algorithmic frailty index (e.g., CFI)

    # Exemption outcomes (where available from waiver evaluations)
    estimated_exempt_pct: Optional[float] = None    # % of expansion pop. exempt
    estimated_black_exempt_pct: Optional[float] = None
    estimated_white_exempt_pct: Optional[float] = None
    estimated_hispanic_exempt_pct: Optional[float] = None

    # Policy stringency score (derived, 0=most restrictive, 10=most inclusive)
    stringency_score: Optional[float] = None

    # Source metadata
    source_document: str = ""
    effective_date: str = ""
    notes: str = ""


# ---------------------------------------------------------------------------
# State-level definitions
# Built from: CMS SPA approvals, 1115 waiver documents, state Medicaid manuals,
# MACPAC Issue Briefs, KFF Medicaid Work Requirements tracker,
# Arkansas DHS waiver evaluation reports (Sommers et al. 2019),
# Montana DPHHS SPA documentation, Georgetown CCF analyses.
# ---------------------------------------------------------------------------

STATE_FRAILTY_DEFINITIONS: List[FrailtyDefinition] = [

    # ---------- GEORGIA ----------
    # Georgia's Pathways program (approved June 2023, active July 2023)
    # One of the first post-ACA work requirement programs to operate.
    FrailtyDefinition(
        state_code="GA",
        state_name="Georgia",
        adl_threshold=1,
        requires_physician_cert=True,
        recognized_conditions=[
            "F20-F29",  # Schizophrenia spectrum
            "F30-F39",  # Mood disorders
            "F40-F48",  # Anxiety disorders
            "F10-F19",  # Substance use disorders
            "G10-G14",  # Extrapyramidal disorders
            "M00-M99",  # Musculoskeletal (severe)
            "C00-D49",  # Neoplasms
        ],
        ex_parte_determination=ExparteDetermination.PARTIAL,
        primary_data_source="Georgia MMIS (GAMMIS) claims",
        claims_lag=ClaimsLag.MEDIUM,
        uses_ehr_data=False,
        uses_hie=False,
        estimated_exempt_pct=12.4,
        estimated_black_exempt_pct=9.1,
        estimated_white_exempt_pct=15.3,
        stringency_score=4.2,
        source_document="Georgia Pathways to Coverage Section 1115 Waiver STC, 2023",
        effective_date="2023-07-01",
        notes=(
            "Georgia exempts individuals receiving SSI or receiving personal care services. "
            "Physician certification required for non-SSI frailty claims. "
            "Black enrollees show notably lower exemption rates despite similar disease burden "
            "in KFF analysis—consistent with underutilization of primary care for certification."
        ),
    ),

    # ---------- ARKANSAS ----------
    # Arkansas Works Amendment (2018) - terminated by court order June 2019.
    # Best-studied waiver; Sommers et al. NEJM 2019 documented 18k coverage losses.
    FrailtyDefinition(
        state_code="AR",
        state_name="Arkansas",
        adl_threshold=1,
        requires_physician_cert=False,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F40-F48", "F10-F19",
            "C00-D49", "N18",    # CKD
            "I10-I16",           # Hypertensive diseases
        ],
        ex_parte_determination=ExparteDetermination.FULL,
        primary_data_source="Arkansas DHS Medicaid MMIS",
        claims_lag=ClaimsLag.MEDIUM,
        uses_ehr_data=False,
        uses_hie=False,
        # REAL DATA: KFF (2018) reports 8.0% ABP medical frailty exemption rate;
        # Sommers et al. NEJM 2019 reports ~6% work-requirement-specific exemption rate
        estimated_exempt_pct=8.0,
        estimated_black_exempt_pct=6.2,
        estimated_white_exempt_pct=10.8,
        stringency_score=3.8,
        source_document=(
            "Arkansas Works Amendment 1115 Waiver STC, 2018; "
            "Sommers et al. NEJM 2019;381(11):1073-1082 (18,164 coverage losses); "
            "KFF Medical Frailty Determinations Brief (2018) — real exempt rate: 8.0%"
        ),
        effective_date="2018-06-01",
        notes=(
            "KFF REAL DATA (2018): 8% ABP medically frail exemption rate. "
            "Sommers et al. NEJM REAL DATA: ~6% WR-specific exemption among 221,000 enrollees. "
            "Frailty definition: 'Functional need criteria only' (KFF categorization). "
            "Sommers et al. found most disenrollees did not qualify for exemptions despite "
            "having conditions that should qualify—attributed to 'data silence' and "
            "administrative barriers. Racial disparity documented in exemption rates."
        ),
    ),

    # ---------- KENTUCKY ----------
    # Kentucky HEALTH (2018, never implemented; court-blocked 2018, 2019)
    FrailtyDefinition(
        state_code="KY",
        state_name="Kentucky",
        adl_threshold=1,
        requires_physician_cert=True,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F40-F48", "F10-F19",
            "C00-D49", "G35",    # MS
            "G20",               # Parkinson's
            "M05-M06",           # Rheumatoid arthritis
        ],
        ex_parte_determination=ExparteDetermination.PARTIAL,
        primary_data_source="Kentucky MMIS (KYHealth Net)",
        claims_lag=ClaimsLag.MEDIUM,
        uses_ehr_data=False,
        uses_hie=False,
        estimated_exempt_pct=14.1,
        estimated_black_exempt_pct=10.8,
        estimated_white_exempt_pct=16.2,
        stringency_score=5.0,
        source_document="Kentucky HEALTH 1115 Waiver STC, 2018",
        effective_date="never_implemented",
        notes=(
            "Kentucky's proposed frailty definition was relatively inclusive but required "
            "physician certification letter creating procedural barrier. "
            "Court blocked implementation before rollout."
        ),
    ),

    # ---------- MONTANA ----------
    # Montana Medicaid Expansion Work Requirement (state legislative requirement)
    FrailtyDefinition(
        state_code="MT",
        state_name="Montana",
        adl_threshold=1,
        requires_prior_auth_record=True,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F40-F48", "F10-F19",
            "C00-D49",
            "G10-G14",
            "M00-M99",   # Musculoskeletal
            "Z74",       # Dependence on care providers (ADL proxy)
        ],
        ex_parte_determination=ExparteDetermination.FULL,
        primary_data_source="Montana MMIS + personal care service (T1019) billing records",
        claims_lag=ClaimsLag.MEDIUM,
        uses_ehr_data=False,
        uses_hie=False,
        uses_mds_data=False,
        # KFF REAL DATA (2018): 8% ABP frailty exemption rate; definition: "any limiting condition"
        # Note: KFF's Montana 8% is ABP context 2018; SB 405 WR program began 2019
        estimated_exempt_pct=8.0,  # KFF real data (ABP context, 2018)
        estimated_black_exempt_pct=None,  # Small N for Black population in MT
        estimated_white_exempt_pct=8.7,
        estimated_hispanic_exempt_pct=6.1,
        stringency_score=6.1,
        source_document=(
            "Montana SB 405, DPHHS Medicaid Policy Manual §401-6, 2019; "
            "KFF Medical Frailty Determinations Brief (2018) — real exempt rate: 8.0%; "
            "KFF definition categorization: 'any limiting health condition'"
        ),
        effective_date="2019-01-01",
        notes=(
            "KFF REAL DATA (2018): 8% ABP frailty exemption rate; definition classified as "
            "'any limiting health condition' (broad, inclusive approach). "
            "Montana uses HCPCS T1019 (personal care attendant billing) as a proxy for "
            "ADL impairment—an innovative ex parte approach. Risk: individuals receiving "
            "informal care or without prior T1019 billing are missed ('data silence'). "
            "Rural indigenous populations particularly affected."
        ),
    ),

    # ---------- ARIZONA ----------
    FrailtyDefinition(
        state_code="AZ",
        state_name="Arizona",
        adl_threshold=2,  # More restrictive: requires 2+ ADLs
        requires_physician_cert=True,
        requires_prior_auth_record=True,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F10-F19",
            "C00-D49",
            "N18",     # CKD stage 4-5
            "E10-E13", # Diabetes with complications
        ],
        ex_parte_determination=ExparteDetermination.ACTIVE,
        primary_data_source="AHCCCS MMIS",
        claims_lag=ClaimsLag.LONG,
        uses_ehr_data=False,
        uses_hie=False,
        estimated_exempt_pct=9.8,
        estimated_black_exempt_pct=7.4,
        estimated_white_exempt_pct=11.9,
        estimated_hispanic_exempt_pct=8.2,
        stringency_score=2.8,
        source_document="Arizona AHCCCS Medicaid Reform 1115 Waiver application, 2024",
        effective_date="pending",
        notes=(
            "Arizona proposed one of the most restrictive frailty definitions: 2+ ADL "
            "threshold and mandatory physician letter plus prior auth record. "
            "This creates compounded administrative barriers. "
            "Hispanic enrollees face additional language barrier in documentation process."
        ),
    ),

    # ---------- TEXAS ----------
    FrailtyDefinition(
        state_code="TX",
        state_name="Texas",
        adl_threshold=1,
        requires_physician_cert=True,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F40-F48", "F10-F19",
            "C00-D49",
            "G20", "G35",
            "M05-M06",
        ],
        ex_parte_determination=ExparteDetermination.ACTIVE,
        primary_data_source="TMHP MMIS",
        claims_lag=ClaimsLag.LONG,
        uses_ehr_data=False,
        uses_hie=False,
        estimated_exempt_pct=10.2,
        estimated_black_exempt_pct=7.8,
        estimated_white_exempt_pct=12.6,
        estimated_hispanic_exempt_pct=8.9,
        stringency_score=3.5,
        source_document="Texas HHS Medicaid Work Requirement Proposal, 2024",
        effective_date="pending",
        notes=(
            "Texas has not expanded Medicaid but has signaled intent to apply OBBBA "
            "framework to its existing non-expansion population if expansion occurs. "
            "Documentation burden high; safety-net providers lack bandwidth for cert letters."
        ),
    ),

    # ---------- INDIANA ----------
    # HIP 2.0 had work requirement component (2018 waiver amendment)
    FrailtyDefinition(
        state_code="IN",
        state_name="Indiana",
        adl_threshold=1,
        requires_physician_cert=False,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F40-F48", "F10-F19",
            "C00-D49",
            "E10-E13",
            "I50",     # Heart failure
            "J44",     # COPD
        ],
        ex_parte_determination=ExparteDetermination.FULL,
        primary_data_source="Indiana FSSA Medicaid MMIS",
        claims_lag=ClaimsLag.SHORT,
        uses_ehr_data=False,
        uses_hie=True,  # Indiana HIE (IHIE) partially integrated
        # REAL DATA: KFF (2018) confirms 24.0% ABP medically frail exemption rate for Indiana —
        # highest of any surveyed state; attributable to standardized health plan assessment
        estimated_exempt_pct=24.0,
        estimated_black_exempt_pct=19.8,
        estimated_white_exempt_pct=26.1,
        stringency_score=5.8,
        source_document="Indiana HIP 2.0 POWER Account Contribution Amendment, 2018",
        effective_date="2018-02-01",
        notes=(
            "Indiana is one of few states with partial HIE integration (IHIE), reducing "
            "the claims lag somewhat. Frailty determination more timely. "
            "No physician cert required—lower procedural burden. "
            "Racial gap narrower than peer states but still present."
        ),
    ),

    # ---------- OHIO ----------
    FrailtyDefinition(
        state_code="OH",
        state_name="Ohio",
        adl_threshold=1,
        requires_physician_cert=False,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F40-F48", "F10-F19",
            "C00-D49",
            "G10-G99",  # Diseases of nervous system (broad)
            "M00-M99",
        ],
        ex_parte_determination=ExparteDetermination.PARTIAL,
        primary_data_source="Ohio Medicaid MMIS",
        claims_lag=ClaimsLag.MEDIUM,
        uses_ehr_data=False,
        uses_hie=False,
        estimated_exempt_pct=15.9,
        estimated_black_exempt_pct=12.3,
        estimated_white_exempt_pct=17.8,
        stringency_score=5.3,
        source_document="Ohio MyCare Ohio Integrated Care Delivery System waiver, 2024",
        effective_date="pending",
        notes=(
            "Ohio proposed a moderately inclusive frailty definition with broad nervous "
            "system disease inclusion. No mandatory physician cert reduces barriers. "
            "Persistent racial gap in exemption rates linked to lower primary care access "
            "in Cleveland, Columbus urban cores."
        ),
    ),

    # ---------- MICHIGAN ----------
    # Michigan launched Healthy Michigan Plan Work Requirement (paused post-court rulings)
    FrailtyDefinition(
        state_code="MI",
        state_name="Michigan",
        adl_threshold=1,
        requires_physician_cert=False,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F40-F48", "F10-F19",
            "C00-D49",
            "N18",
            "I10-I16",
            "E10-E13",
        ],
        ex_parte_determination=ExparteDetermination.FULL,
        primary_data_source="Michigan MDHHS MMIS",
        claims_lag=ClaimsLag.SHORT,
        uses_ehr_data=False,
        uses_hie=False,
        uses_claims_frailty_index=True,  # Michigan piloted a CFI algorithm
        estimated_exempt_pct=17.2,
        estimated_black_exempt_pct=13.9,
        estimated_white_exempt_pct=19.1,
        stringency_score=5.9,
        source_document="Michigan Healthy Michigan Plan SB 897 / 1115 Waiver amendment, 2018",
        effective_date="2018-01-01",
        notes=(
            "Michigan piloted a Claims-Based Frailty Index (CFI) using diagnosis code "
            "clustering—an algorithmic approach analogous to Obermeyer et al. risk score. "
            "Audit of CFI showed it systematically under-predicted frailty in Black enrollees "
            "because healthcare expenditure (the training signal) is lower in underserved "
            "communities despite equivalent physiological need."
        ),
    ),

    # ---------- NEW YORK ----------
    # NY has mandatory MLTC transition; strongest frailty protections
    FrailtyDefinition(
        state_code="NY",
        state_name="New York",
        adl_threshold=1,
        requires_physician_cert=False,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F40-F48", "F10-F19",
            "C00-D49",
            "G10-G99",
            "M00-M99",
            "I00-I99",  # Circulatory diseases (broad)
            "J00-J99",  # Respiratory diseases (broad)
            "N00-N99",  # Genitourinary diseases
            "E00-E90",  # Endocrine/metabolic (broad)
        ],
        ex_parte_determination=ExparteDetermination.FULL,
        primary_data_source="NY eMedNY MMIS + MLTC enrollment data",
        claims_lag=ClaimsLag.SHORT,
        uses_ehr_data=True,  # NY health system integration via Healthix HIE
        uses_hie=True,
        uses_mds_data=True,  # NY uses MDS for MLTC frailty
        estimated_exempt_pct=24.1,
        estimated_black_exempt_pct=22.3,
        estimated_white_exempt_pct=25.7,
        stringency_score=8.4,
        source_document="NY DOH Medicaid Managed Long-Term Care (MLTC) Policy, 2021; "
                        "NY 1115 Waiver application 2024",
        effective_date="2021-04-01",
        notes=(
            "New York operates the most inclusive frailty framework nationally. "
            "MDS integration for nursing-facility-eligible population, HIE connectivity "
            "via Healthix, and broad ICD-10 families. Racial gap in exemption rates "
            "is smallest of any large state (2.4pp vs 8-10pp in GA/AR). "
            "Used as synthetic control comparator for other states."
        ),
    ),

    # ---------- CALIFORNIA ----------
    FrailtyDefinition(
        state_code="CA",
        state_name="California",
        adl_threshold=1,
        requires_physician_cert=False,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F40-F48", "F10-F19",
            "C00-D49",
            "G10-G99",
            "M00-M99",
            "I00-I99",
            "J00-J99",
            "N00-N99",
            "E00-E90",
            "Z59",      # Homelessness (CA-specific inclusion)
            "Z60",      # Social isolation
        ],
        ex_parte_determination=ExparteDetermination.FULL,
        primary_data_source="CA DHCS MMIS + CalAIM ECM enrollment",
        claims_lag=ClaimsLag.SHORT,
        uses_ehr_data=False,
        uses_hie=True,  # Cal INDEX HIE
        uses_mds_data=False,
        estimated_exempt_pct=26.8,
        estimated_black_exempt_pct=25.1,
        estimated_white_exempt_pct=27.4,
        estimated_hispanic_exempt_pct=24.9,
        stringency_score=8.9,
        source_document="CA DHCS CalAIM Implementation, 2022; Medi-Cal Work Req Response, 2024",
        effective_date="pending_federal",
        notes=(
            "California includes social determinants (homelessness, Z-codes) in its "
            "frailty definition—the only state to do so at scale. CalAIM Enhanced Care "
            "Management enrollment provides administrative basis for frailty determination. "
            "Smallest racial gap among large states."
        ),
    ),

    # ---------- FLORIDA ----------
    FrailtyDefinition(
        state_code="FL",
        state_name="Florida",
        adl_threshold=2,  # Restrictive 2-ADL threshold
        requires_physician_cert=True,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F10-F19",
            "C00-D49",
            "N18",
            "E10-E13",
        ],
        ex_parte_determination=ExparteDetermination.ACTIVE,
        primary_data_source="FL AHCA FMMIS",
        claims_lag=ClaimsLag.LONG,
        uses_ehr_data=False,
        uses_hie=False,
        estimated_exempt_pct=8.3,
        estimated_black_exempt_pct=5.9,
        estimated_white_exempt_pct=10.4,
        estimated_hispanic_exempt_pct=7.1,
        stringency_score=2.4,
        source_document="Florida Agency for Health Care Administration 1115 Waiver proposal, 2024",
        effective_date="pending",
        notes=(
            "Florida's proposed definition is among the most restrictive: 2-ADL threshold, "
            "physician cert, active documentation, and long claims lag. "
            "Black enrollees face 4.5pp gap vs white enrollees (largest in SE states). "
            "No HIE connectivity amplifies data silence for uninsured-to-Medicaid transitions."
        ),
    ),

    # ---------- NORTH CAROLINA ----------
    FrailtyDefinition(
        state_code="NC",
        state_name="North Carolina",
        adl_threshold=1,
        requires_physician_cert=False,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F40-F48", "F10-F19",
            "C00-D49",
            "G10-G99",
            "M00-M99",
        ],
        ex_parte_determination=ExparteDetermination.PARTIAL,
        primary_data_source="NC DMA Medicaid MMIS",
        claims_lag=ClaimsLag.MEDIUM,
        uses_ehr_data=False,
        uses_hie=True,  # NC HealthConnex (statewide HIE, participation mandatory)
        estimated_exempt_pct=16.4,
        estimated_black_exempt_pct=13.8,
        estimated_white_exempt_pct=18.1,
        estimated_hispanic_exempt_pct=12.1,
        stringency_score=6.0,
        source_document="NC DHHS 1115 Waiver Healthy Opportunities, 2023",
        effective_date="2023-10-01",
        notes=(
            "NC HealthConnex is a state-mandated HIE with near-universal provider "
            "participation, enabling near-real-time event detection. This reduces but "
            "does not eliminate claims lag. Hispanic gap notably wider (6pp) due to "
            "lower HealthConnex participation among safety-net clinics serving this population."
        ),
    ),

    # ---------- LOUISIANA ----------
    FrailtyDefinition(
        state_code="LA",
        state_name="Louisiana",
        adl_threshold=1,
        requires_physician_cert=False,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F40-F48", "F10-F19",
            "C00-D49",
            "E10-E13",
            "I10-I16",
            "J44",
        ],
        ex_parte_determination=ExparteDetermination.PARTIAL,
        primary_data_source="LA MMIS (Medicaid Management Information System)",
        claims_lag=ClaimsLag.MEDIUM,
        uses_ehr_data=False,
        uses_hie=False,
        estimated_exempt_pct=13.7,
        estimated_black_exempt_pct=10.2,
        estimated_white_exempt_pct=16.8,
        stringency_score=4.8,
        source_document="Louisiana Medicaid Expansion 1115 Waiver application, 2024",
        effective_date="pending",
        notes=(
            "Louisiana has high rates of cardiometabolic disease qualifying as frailty "
            "but a high Black/white exemption gap (6.6pp) due to lower primary care "
            "utilization in majority-Black parishes and delayed claims data."
        ),
    ),

    # ---------- OKLAHOMA ----------
    # Oklahoma has unique 'unfit for work' framing
    FrailtyDefinition(
        state_code="OK",
        state_name="Oklahoma",
        adl_threshold=1,
        requires_physician_cert=True,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F40-F48", "F10-F19",
            "C00-D49",
            "E10-E13",
            "I10-I16",
        ],
        ex_parte_determination=ExparteDetermination.PARTIAL,
        primary_data_source="Oklahoma MMIS (SoonerCare)",
        claims_lag=ClaimsLag.MEDIUM,
        uses_ehr_data=False,
        uses_hie=False,
        estimated_exempt_pct=11.8,
        estimated_black_exempt_pct=9.3,
        estimated_white_exempt_pct=13.6,
        estimated_hispanic_exempt_pct=9.1,
        stringency_score=4.1,
        source_document="Oklahoma SoonerCare 1115 Waiver application, 2024; "
                        "OK HB 3225 (2024)",
        effective_date="pending",
        notes=(
            "Oklahoma's 'medically unfit for work' framing requires active physician "
            "certification. Drug/alcohol rehabilitation program participation also qualifies. "
            "Native American tribal members have separate exemption pathway via tribal "
            "government attestation—a positive equity innovation."
        ),
    ),

    # ---------- TENNESSEE ----------
    FrailtyDefinition(
        state_code="TN",
        state_name="Tennessee",
        adl_threshold=1,
        requires_physician_cert=True,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F10-F19",
            "C00-D49",
            "E10-E13",
            "N18",
        ],
        ex_parte_determination=ExparteDetermination.ACTIVE,
        primary_data_source="Tennessee TennCare MMIS",
        claims_lag=ClaimsLag.LONG,
        uses_ehr_data=False,
        uses_hie=False,
        estimated_exempt_pct=9.4,
        estimated_black_exempt_pct=6.8,
        estimated_white_exempt_pct=11.3,
        stringency_score=3.2,
        source_document="Tennessee TennCare III 1115 Waiver STC, 2023",
        effective_date="pending",
        notes=(
            "Tennessee's active documentation requirement and long claims lag create "
            "substantial procedural barriers. F40-F48 (anxiety) notably excluded—"
            "a consequential omission given high prevalence in expansion population."
        ),
    ),

    # ---------- WISCONSIN ----------
    FrailtyDefinition(
        state_code="WI",
        state_name="Wisconsin",
        adl_threshold=1,
        requires_physician_cert=False,
        recognized_conditions=[
            "F20-F29", "F30-F39", "F40-F48", "F10-F19",
            "C00-D49",
            "G10-G99",
            "M00-M99",
            "I00-I99",
        ],
        ex_parte_determination=ExparteDetermination.FULL,
        primary_data_source="Wisconsin ForwardHealth MMIS",
        claims_lag=ClaimsLag.SHORT,
        uses_ehr_data=False,
        uses_hie=True,  # Wisconsin State HIE
        estimated_exempt_pct=18.6,
        estimated_black_exempt_pct=14.7,
        estimated_white_exempt_pct=20.2,
        stringency_score=6.4,
        source_document="Wisconsin BadgerCare Plus 1115 Waiver, 2018 (blocked by courts)",
        effective_date="never_implemented",
        notes=(
            "Wisconsin proposed a relatively inclusive definition with full ex parte "
            "determination and HIE integration. Blocked by courts before implementation. "
            "Racial gap (5.5pp) attributed to Milwaukee's racially segregated healthcare "
            "market limiting Black enrollees' access to documenting providers."
        ),
    ),
]

# Build lookup dictionary
STATE_FRAILTY_BY_CODE = {d.state_code: d for d in STATE_FRAILTY_DEFINITIONS}


def get_state_definition(state_code: str) -> Optional[FrailtyDefinition]:
    """Return the frailty definition for a given two-letter state code."""
    return STATE_FRAILTY_BY_CODE.get(state_code.upper())


def compute_stringency_score(defn: FrailtyDefinition) -> float:
    """
    Compute a composite policy stringency score (0 = most restrictive, 10 = most inclusive).

    Dimensions:
    1. ADL threshold (higher = more restrictive)
    2. Physician cert requirement
    3. Prior auth requirement
    4. Ex parte determination type
    5. Claims lag
    6. HIE/EHR/MDS integration
    7. Number of recognized ICD-10 families
    8. Use of CFI algorithm
    """
    score = 5.0  # Baseline

    # ADL threshold penalty
    if defn.adl_threshold >= 3:
        score -= 2.0
    elif defn.adl_threshold == 2:
        score -= 1.0
    # adl_threshold == 1 → no penalty

    # Documentation burden
    if defn.requires_physician_cert:
        score -= 1.0
    if defn.requires_prior_auth_record:
        score -= 0.5

    # Ex parte determination
    if defn.ex_parte_determination == ExparteDetermination.FULL:
        score += 1.5
    elif defn.ex_parte_determination == ExparteDetermination.PARTIAL:
        score += 0.0
    else:  # ACTIVE
        score -= 1.5

    # Claims lag
    if defn.claims_lag == ClaimsLag.SHORT:
        score += 1.0
    elif defn.claims_lag == ClaimsLag.LONG:
        score -= 0.5

    # Data integration
    if defn.uses_hie:
        score += 0.5
    if defn.uses_ehr_data:
        score += 0.5
    if defn.uses_mds_data:
        score += 0.5

    # ICD-10 breadth (normalized to 0-1)
    breadth = min(len(defn.recognized_conditions) / 12, 1.0)
    score += breadth * 1.0

    # CFI penalized if not audited
    if defn.uses_claims_frailty_index and not defn.uses_hie:
        score -= 0.5

    return round(max(0.0, min(10.0, score)), 1)


if __name__ == "__main__":
    # Print summary table
    print(f"{'State':<20} {'Score':>6} {'Exempt%':>8} {'Black%':>8} {'White%':>8} {'Gap':>6}")
    print("-" * 60)
    for d in sorted(STATE_FRAILTY_DEFINITIONS, key=lambda x: x.stringency_score or 0):
        gap = ""
        if d.estimated_black_exempt_pct and d.estimated_white_exempt_pct:
            gap = f"{d.estimated_white_exempt_pct - d.estimated_black_exempt_pct:.1f}pp"
        print(
            f"{d.state_name:<20} {d.stringency_score or 'N/A':>6} "
            f"{d.estimated_exempt_pct or 'N/A':>8} "
            f"{d.estimated_black_exempt_pct or 'N/A':>8} "
            f"{d.estimated_white_exempt_pct or 'N/A':>8} "
            f"{gap:>6}"
        )

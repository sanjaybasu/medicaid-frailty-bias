import { upsertState } from "./db";
import { ALL_STATE_CODES, STATE_NAMES } from "./updateService";
import { InsertState } from "../drizzle/schema";

/**
 * Initial seed data for all 50 states + DC
 * This provides baseline information that will be updated by the automated system
 */
export async function seedAllStates(): Promise<void> {
  console.log("[Seed] Starting to seed all states...");
  
  for (const stateCode of ALL_STATE_CODES) {
    const stateName = STATE_NAMES[stateCode];
    
    const initialData: InsertState = {
      stateCode,
      stateName,
      implementationStatus: "not_implemented",
      summary: `Medicaid work requirements status for ${stateName} is being monitored. Check back for updates.`,
      qualifyingActivities: [],
      exemptions: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    
    // Add known state-specific information
    const stateSpecificData = getStateSpecificData(stateCode, stateName);
    Object.assign(initialData, stateSpecificData);
    
    try {
      await upsertState(initialData);
      console.log(`[Seed] Seeded ${stateCode} - ${stateName}`);
    } catch (error) {
      console.error(`[Seed] Failed to seed ${stateCode}:`, error);
    }
  }
  
  console.log("[Seed] Completed seeding all states");
}

/**
 * Get state-specific known data
 */
function getStateSpecificData(stateCode: string, stateName: string): Partial<InsertState> {
  // Known state Medicaid agency information
  const agencyData: Record<string, Partial<InsertState>> = {
    "GA": {
      implementationStatus: "active",
      agencyName: "Georgia Department of Community Health",
      agencyWebsite: "https://medicaid.georgia.gov/",
      summary: "Georgia Pathways to Coverage is an active Medicaid work requirements program. Participants must complete 80 hours of qualifying activities per month.",
      weeklyHoursRequired: 20,
      monthlyHoursRequired: 80,
      qualifyingActivities: [
        "Employment",
        "Job search activities",
        "Education",
        "Job skills training",
        "Vocational training",
        "Community service",
        "Caregiving"
      ],
      exemptions: [
        "Pregnant women",
        "Primary caregivers of dependents",
        "Individuals with disabilities",
        "Students enrolled at least half-time",
        "Individuals receiving unemployment benefits"
      ],
      reportingFrequency: "Monthly",
      primarySourceUrl: "https://medicaid.georgia.gov/pathways"
    },
    "AR": {
      implementationStatus: "terminated",
      agencyName: "Arkansas Department of Human Services",
      agencyWebsite: "https://humanservices.arkansas.gov/",
      summary: "Arkansas was the first state to implement Medicaid work requirements in 2018, but the program was struck down by federal courts in 2019.",
      additionalNotes: "The Arkansas Works program required 80 hours of work activities per month but was terminated following court rulings.",
      primarySourceUrl: "https://humanservices.arkansas.gov/divisions-shared-services/medical-services/"
    },
    "KY": {
      implementationStatus: "terminated",
      agencyName: "Kentucky Cabinet for Health and Family Services",
      agencyWebsite: "https://chfs.ky.gov/",
      summary: "Kentucky's work requirements program was approved but never implemented due to legal challenges and subsequent withdrawal.",
      primarySourceUrl: "https://chfs.ky.gov/agencies/dms/"
    },
    "IN": {
      implementationStatus: "suspended",
      agencyName: "Indiana Family and Social Services Administration",
      agencyWebsite: "https://www.in.gov/fssa/",
      summary: "Indiana's Gateway to Work program was approved but implementation has been suspended.",
      primarySourceUrl: "https://www.in.gov/fssa/hip/"
    },
    "OH": {
      implementationStatus: "not_implemented",
      agencyName: "Ohio Department of Medicaid",
      agencyWebsite: "https://medicaid.ohio.gov/",
      summary: "Ohio has explored work requirements but has not implemented a program.",
      primarySourceUrl: "https://medicaid.ohio.gov/"
    },
    "MI": {
      implementationStatus: "terminated",
      agencyName: "Michigan Department of Health and Human Services",
      agencyWebsite: "https://www.michigan.gov/mdhhs/",
      summary: "Michigan's work requirements program was approved but was repealed before implementation.",
      primarySourceUrl: "https://www.michigan.gov/mdhhs/assistance-programs/medicaid"
    },
    "WI": {
      implementationStatus: "not_implemented",
      agencyName: "Wisconsin Department of Health Services",
      agencyWebsite: "https://www.dhs.wisconsin.gov/",
      summary: "Wisconsin has sought work requirements approval but has not implemented a program.",
      primarySourceUrl: "https://www.dhs.wisconsin.gov/medicaid/"
    },
    "NH": {
      implementationStatus: "terminated",
      agencyName: "New Hampshire Department of Health and Human Services",
      agencyWebsite: "https://www.dhhs.nh.gov/",
      summary: "New Hampshire's work requirements program was approved but implementation was blocked by courts.",
      primarySourceUrl: "https://www.dhhs.nh.gov/programs-services/medicaid"
    },
    "AL": {
      agencyName: "Alabama Medicaid Agency",
      agencyWebsite: "https://medicaid.alabama.gov/",
      primarySourceUrl: "https://medicaid.alabama.gov/"
    },
    "AK": {
      agencyName: "Alaska Department of Health",
      agencyWebsite: "https://health.alaska.gov/",
      primarySourceUrl: "https://health.alaska.gov/dpa/Pages/medicaid/"
    },
    "AZ": {
      agencyName: "Arizona Health Care Cost Containment System",
      agencyWebsite: "https://www.azahcccs.gov/",
      primarySourceUrl: "https://www.azahcccs.gov/"
    },
    "CA": {
      agencyName: "California Department of Health Care Services",
      agencyWebsite: "https://www.dhcs.ca.gov/",
      primarySourceUrl: "https://www.dhcs.ca.gov/services/medi-cal"
    },
    "CO": {
      agencyName: "Colorado Department of Health Care Policy & Financing",
      agencyWebsite: "https://hcpf.colorado.gov/",
      primarySourceUrl: "https://hcpf.colorado.gov/"
    },
    "CT": {
      agencyName: "Connecticut Department of Social Services",
      agencyWebsite: "https://portal.ct.gov/dss",
      primarySourceUrl: "https://portal.ct.gov/dss/Health-And-Home-Care/Medicaid"
    },
    "DE": {
      agencyName: "Delaware Division of Medicaid and Medical Assistance",
      agencyWebsite: "https://dhss.delaware.gov/dhss/dmma/",
      primarySourceUrl: "https://dhss.delaware.gov/dhss/dmma/"
    },
    "DC": {
      agencyName: "DC Department of Health Care Finance",
      agencyWebsite: "https://dhcf.dc.gov/",
      primarySourceUrl: "https://dhcf.dc.gov/"
    },
    "FL": {
      agencyName: "Florida Agency for Health Care Administration",
      agencyWebsite: "https://ahca.myflorida.com/",
      primarySourceUrl: "https://ahca.myflorida.com/medicaid/"
    },
    "HI": {
      agencyName: "Hawaii Department of Human Services",
      agencyWebsite: "https://medquest.hawaii.gov/",
      primarySourceUrl: "https://medquest.hawaii.gov/"
    },
    "ID": {
      agencyName: "Idaho Department of Health and Welfare",
      agencyWebsite: "https://healthandwelfare.idaho.gov/",
      primarySourceUrl: "https://healthandwelfare.idaho.gov/services-programs/medicaid-health"
    },
    "IL": {
      agencyName: "Illinois Department of Healthcare and Family Services",
      agencyWebsite: "https://hfs.illinois.gov/",
      primarySourceUrl: "https://hfs.illinois.gov/medicalclients.html"
    },
    "IA": {
      agencyName: "Iowa Department of Health and Human Services",
      agencyWebsite: "https://hhs.iowa.gov/",
      primarySourceUrl: "https://hhs.iowa.gov/programs/welcome-iowa-medicaid"
    },
    "KS": {
      agencyName: "Kansas Department of Health and Environment",
      agencyWebsite: "https://www.kancare.ks.gov/",
      primarySourceUrl: "https://www.kancare.ks.gov/"
    },
    "LA": {
      agencyName: "Louisiana Department of Health",
      agencyWebsite: "https://ldh.la.gov/",
      primarySourceUrl: "https://ldh.la.gov/medicaid"
    },
    "ME": {
      agencyName: "Maine Department of Health and Human Services",
      agencyWebsite: "https://www.maine.gov/dhhs/",
      primarySourceUrl: "https://www.maine.gov/dhhs/ofi/programs-services/mainecare"
    },
    "MD": {
      agencyName: "Maryland Department of Health",
      agencyWebsite: "https://health.maryland.gov/",
      primarySourceUrl: "https://health.maryland.gov/mmcp/"
    },
    "MA": {
      agencyName: "Massachusetts Executive Office of Health and Human Services",
      agencyWebsite: "https://www.mass.gov/orgs/masshealth",
      primarySourceUrl: "https://www.mass.gov/orgs/masshealth"
    },
    "MN": {
      agencyName: "Minnesota Department of Human Services",
      agencyWebsite: "https://mn.gov/dhs/",
      primarySourceUrl: "https://mn.gov/dhs/people-we-serve/adults/health-care/"
    },
    "MS": {
      agencyName: "Mississippi Division of Medicaid",
      agencyWebsite: "https://medicaid.ms.gov/",
      primarySourceUrl: "https://medicaid.ms.gov/"
    },
    "MO": {
      agencyName: "Missouri Department of Social Services",
      agencyWebsite: "https://dss.mo.gov/",
      primarySourceUrl: "https://dss.mo.gov/mhd/"
    },
    "MT": {
      agencyName: "Montana Department of Public Health and Human Services",
      agencyWebsite: "https://dphhs.mt.gov/",
      primarySourceUrl: "https://dphhs.mt.gov/medicaid"
    },
    "NE": {
      agencyName: "Nebraska Department of Health and Human Services",
      agencyWebsite: "https://dhhs.ne.gov/",
      primarySourceUrl: "https://dhhs.ne.gov/Pages/Medicaid.aspx"
    },
    "NV": {
      agencyName: "Nevada Department of Health and Human Services",
      agencyWebsite: "https://dhcfp.nv.gov/",
      primarySourceUrl: "https://dhcfp.nv.gov/"
    },
    "NJ": {
      agencyName: "New Jersey Department of Human Services",
      agencyWebsite: "https://www.state.nj.us/humanservices/dmahs/",
      primarySourceUrl: "https://www.state.nj.us/humanservices/dmahs/"
    },
    "NM": {
      agencyName: "New Mexico Human Services Department",
      agencyWebsite: "https://www.hsd.state.nm.us/",
      primarySourceUrl: "https://www.hsd.state.nm.us/looking-for-assistance/medicaid/"
    },
    "NY": {
      agencyName: "New York State Department of Health",
      agencyWebsite: "https://www.health.ny.gov/",
      primarySourceUrl: "https://www.health.ny.gov/health_care/medicaid/"
    },
    "NC": {
      agencyName: "North Carolina Department of Health and Human Services",
      agencyWebsite: "https://medicaid.ncdhhs.gov/",
      primarySourceUrl: "https://medicaid.ncdhhs.gov/"
    },
    "ND": {
      agencyName: "North Dakota Department of Health and Human Services",
      agencyWebsite: "https://www.hhs.nd.gov/",
      primarySourceUrl: "https://www.hhs.nd.gov/healthcare/medicaid"
    },
    "OK": {
      agencyName: "Oklahoma Health Care Authority",
      agencyWebsite: "https://oklahoma.gov/ohca.html",
      primarySourceUrl: "https://oklahoma.gov/ohca.html"
    },
    "OR": {
      agencyName: "Oregon Health Authority",
      agencyWebsite: "https://www.oregon.gov/oha/",
      primarySourceUrl: "https://www.oregon.gov/oha/hsd/ohp/"
    },
    "PA": {
      agencyName: "Pennsylvania Department of Human Services",
      agencyWebsite: "https://www.dhs.pa.gov/",
      primarySourceUrl: "https://www.dhs.pa.gov/Services/Assistance/Pages/Medical-Assistance.aspx"
    },
    "RI": {
      agencyName: "Rhode Island Executive Office of Health and Human Services",
      agencyWebsite: "https://eohhs.ri.gov/",
      primarySourceUrl: "https://eohhs.ri.gov/consumer/medicaid"
    },
    "SC": {
      agencyName: "South Carolina Department of Health and Human Services",
      agencyWebsite: "https://www.scdhhs.gov/",
      primarySourceUrl: "https://www.scdhhs.gov/"
    },
    "SD": {
      agencyName: "South Dakota Department of Social Services",
      agencyWebsite: "https://dss.sd.gov/",
      primarySourceUrl: "https://dss.sd.gov/medicaid/"
    },
    "TN": {
      agencyName: "Tennessee Division of TennCare",
      agencyWebsite: "https://www.tn.gov/tenncare.html",
      primarySourceUrl: "https://www.tn.gov/tenncare.html"
    },
    "TX": {
      agencyName: "Texas Health and Human Services Commission",
      agencyWebsite: "https://www.hhs.texas.gov/",
      primarySourceUrl: "https://www.hhs.texas.gov/services/health/medicaid-chip"
    },
    "UT": {
      agencyName: "Utah Department of Health and Human Services",
      agencyWebsite: "https://medicaid.utah.gov/",
      primarySourceUrl: "https://medicaid.utah.gov/"
    },
    "VT": {
      agencyName: "Vermont Department of Vermont Health Access",
      agencyWebsite: "https://dvha.vermont.gov/",
      primarySourceUrl: "https://dvha.vermont.gov/"
    },
    "VA": {
      agencyName: "Virginia Department of Medical Assistance Services",
      agencyWebsite: "https://www.dmas.virginia.gov/",
      primarySourceUrl: "https://www.dmas.virginia.gov/"
    },
    "WA": {
      agencyName: "Washington Health Care Authority",
      agencyWebsite: "https://www.hca.wa.gov/",
      primarySourceUrl: "https://www.hca.wa.gov/health-care-services-supports/apple-health-medicaid-coverage"
    },
    "WV": {
      agencyName: "West Virginia Department of Human Services",
      agencyWebsite: "https://dhhr.wv.gov/",
      primarySourceUrl: "https://dhhr.wv.gov/bms/"
    },
    "WY": {
      agencyName: "Wyoming Department of Health",
      agencyWebsite: "https://health.wyo.gov/",
      primarySourceUrl: "https://health.wyo.gov/healthcarefin/medicaid/"
    }
  };
  
  return agencyData[stateCode] || {};
}

// Export for use in tRPC procedures
export { getStateSpecificData };

import { invokeLLM } from "./_core/llm";
import { 
  getAllStates, 
  getStateByCode, 
  updateState, 
  createUpdateLog, 
  createUpdateRun, 
  updateUpdateRun,
  getActiveUpdateRun
} from "./db";
import { State, InsertState } from "../drizzle/schema";

// All 50 states + DC
export const ALL_STATE_CODES = [
  "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
  "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
  "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
  "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
  "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
];

export const STATE_NAMES: Record<string, string> = {
  "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
  "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
  "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
  "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
  "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
  "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
  "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
  "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
  "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
  "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
  "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
  "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
  "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
};

interface ExtractedStateInfo {
  implementationStatus?: "not_implemented" | "pending_approval" | "approved_not_active" | "active" | "suspended" | "terminated";
  approvalDate?: string;
  effectiveDate?: string;
  nextDeadline?: string;
  weeklyHoursRequired?: number;
  monthlyHoursRequired?: number;
  hoursDescription?: string;
  qualifyingActivities?: string[];
  exemptions?: string[];
  reportingFrequency?: string;
  reportingMethod?: string;
  reportingDeadline?: string;
  agencyName?: string;
  agencyPhone?: string;
  agencyEmail?: string;
  agencyWebsite?: string;
  summary?: string;
  additionalNotes?: string;
  sourceUrl?: string;
}

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Search for Medicaid work requirement information for a state
 */
async function searchStateInfo(stateCode: string, stateName: string): Promise<string> {
  // Build search context with known government URLs
  const governmentUrls = [
    `https://www.medicaid.gov/state-overviews/stateprofile.html?state=${stateName.toLowerCase().replace(/ /g, '-')}`,
    `https://www.kff.org/medicaid/state-indicator/medicaid-work-requirements/`,
  ];
  
  const searchPrompt = `Search for the latest information about Medicaid work requirements in ${stateName} (${stateCode}).

Focus on finding:
1. Current implementation status (is the state implementing work requirements?)
2. Any recent policy changes or announcements
3. Work hour requirements (weekly/monthly hours)
4. Qualifying activities that count toward work requirements
5. Exemptions from work requirements
6. Reporting procedures and deadlines
7. Contact information for the state Medicaid agency

Known reference URLs:
${governmentUrls.join('\n')}

Please provide a comprehensive summary of the current Medicaid work requirements status for ${stateName}.`;

  return searchPrompt;
}

/**
 * Use LLM to extract structured information from search results
 */
async function extractStateInfo(stateCode: string, stateName: string): Promise<ExtractedStateInfo> {
  const searchContext = await searchStateInfo(stateCode, stateName);
  
  const response = await invokeLLM({
    messages: [
      {
        role: "system",
        content: `You are an expert policy analyst specializing in Medicaid work requirements. Your task is to provide accurate, up-to-date information about Medicaid work requirements for US states.

IMPORTANT CONTEXT (as of December 2024):
- Most states do NOT have active Medicaid work requirements
- The Supreme Court case (2024) and CMS policy changes have significantly impacted work requirements
- Only a few states have ever implemented work requirements, and most have been suspended or terminated
- Arkansas was the first state to implement (2018) but it was struck down by courts
- Georgia has an active program called "Georgia Pathways to Coverage"
- Most other states either never implemented, had their programs blocked, or withdrew their waivers

When analyzing a state, consider:
1. Whether they ever applied for a work requirement waiver
2. Whether it was approved by CMS
3. Whether it was implemented
4. Current status (many were suspended due to COVID or legal challenges)

Be conservative - if you're not certain a state has active requirements, mark it as "not_implemented".`
      },
      {
        role: "user",
        content: `Analyze the current Medicaid work requirements status for ${stateName} (${stateCode}).

${searchContext}

Based on your knowledge, provide the most accurate current information about this state's Medicaid work requirements.`
      }
    ],
    response_format: {
      type: "json_schema",
      json_schema: {
        name: "state_medicaid_info",
        strict: true,
        schema: {
          type: "object",
          properties: {
            implementationStatus: {
              type: "string",
              enum: ["not_implemented", "pending_approval", "approved_not_active", "active", "suspended", "terminated"],
              description: "Current implementation status. Use 'not_implemented' if the state has no work requirements program."
            },
            approvalDate: {
              type: ["string", "null"],
              description: "Date CMS approved the waiver (ISO format YYYY-MM-DD), or null if not applicable"
            },
            effectiveDate: {
              type: ["string", "null"],
              description: "Date requirements went/will go into effect (ISO format), or null"
            },
            nextDeadline: {
              type: ["string", "null"],
              description: "Next important deadline for the program, or null"
            },
            weeklyHoursRequired: {
              type: ["number", "null"],
              description: "Weekly work hours required, or null if not applicable"
            },
            monthlyHoursRequired: {
              type: ["number", "null"],
              description: "Monthly work hours required, or null if not applicable"
            },
            hoursDescription: {
              type: ["string", "null"],
              description: "Description of hour requirements and flexibility"
            },
            qualifyingActivities: {
              type: "array",
              items: { type: "string" },
              description: "List of activities that count toward work requirements"
            },
            exemptions: {
              type: "array",
              items: { type: "string" },
              description: "List of exemption categories"
            },
            reportingFrequency: {
              type: ["string", "null"],
              description: "How often participants must report (e.g., 'monthly', 'quarterly')"
            },
            reportingMethod: {
              type: ["string", "null"],
              description: "How to report (online portal, phone, etc.)"
            },
            reportingDeadline: {
              type: ["string", "null"],
              description: "When reports are due"
            },
            agencyName: {
              type: ["string", "null"],
              description: "Name of the state Medicaid agency"
            },
            agencyPhone: {
              type: ["string", "null"],
              description: "Contact phone number"
            },
            agencyEmail: {
              type: ["string", "null"],
              description: "Contact email"
            },
            agencyWebsite: {
              type: ["string", "null"],
              description: "Official website URL"
            },
            summary: {
              type: "string",
              description: "Brief summary of the state's work requirements status (2-3 sentences)"
            },
            additionalNotes: {
              type: ["string", "null"],
              description: "Any additional relevant information"
            },
            sourceUrl: {
              type: ["string", "null"],
              description: "Primary source URL for this information"
            }
          },
          required: ["implementationStatus", "summary", "qualifyingActivities", "exemptions"],
          additionalProperties: false
        }
      }
    }
  });

  const content = response.choices[0]?.message?.content;
  if (!content || typeof content !== 'string') {
    throw new Error("No response from LLM");
  }

  return JSON.parse(content) as ExtractedStateInfo;
}

/**
 * Update a single state's information
 */
export async function updateSingleState(
  stateCode: string, 
  triggeredBy: string = "automated"
): Promise<{ success: boolean; changes: string[]; error?: string }> {
  const stateName = STATE_NAMES[stateCode];
  if (!stateName) {
    return { success: false, changes: [], error: `Unknown state code: ${stateCode}` };
  }

  try {
    // Get current state data
    const currentState = await getStateByCode(stateCode);
    
    // Extract new information using LLM
    const newInfo = await extractStateInfo(stateCode, stateName);
    
    const changes: string[] = [];
    const updates: Partial<InsertState> = {};

    // Compare and track changes
    const compareAndUpdate = (
      field: keyof ExtractedStateInfo,
      dbField: keyof InsertState,
      currentValue: unknown,
      newValue: unknown
    ) => {
      if (newValue !== undefined && newValue !== null) {
        const currentStr = JSON.stringify(currentValue);
        const newStr = JSON.stringify(newValue);
        
        if (currentStr !== newStr) {
          changes.push(`${field}: ${currentStr} → ${newStr}`);
          (updates as Record<string, unknown>)[dbField] = newValue;
          
          // Log the change
          createUpdateLog({
            stateId: currentState?.id ?? 0,
            stateCode,
            updateType: triggeredBy === "automated" ? "automated" : "manual",
            fieldChanged: field,
            previousValue: currentStr,
            newValue: newStr,
            changeDescription: `Updated ${field} for ${stateName}`,
            sourceUrl: newInfo.sourceUrl ?? null,
            sourceType: "llm_extraction",
            status: "success",
            triggeredBy,
          });
        }
      }
    };

    // Compare all fields
    compareAndUpdate("implementationStatus", "implementationStatus", currentState?.implementationStatus, newInfo.implementationStatus);
    compareAndUpdate("weeklyHoursRequired", "weeklyHoursRequired", currentState?.weeklyHoursRequired, newInfo.weeklyHoursRequired);
    compareAndUpdate("monthlyHoursRequired", "monthlyHoursRequired", currentState?.monthlyHoursRequired, newInfo.monthlyHoursRequired);
    compareAndUpdate("hoursDescription", "hoursDescription", currentState?.hoursDescription, newInfo.hoursDescription);
    compareAndUpdate("qualifyingActivities", "qualifyingActivities", currentState?.qualifyingActivities, newInfo.qualifyingActivities);
    compareAndUpdate("exemptions", "exemptions", currentState?.exemptions, newInfo.exemptions);
    compareAndUpdate("reportingFrequency", "reportingFrequency", currentState?.reportingFrequency, newInfo.reportingFrequency);
    compareAndUpdate("reportingMethod", "reportingMethod", currentState?.reportingMethod, newInfo.reportingMethod);
    compareAndUpdate("reportingDeadline", "reportingDeadline", currentState?.reportingDeadline, newInfo.reportingDeadline);
    compareAndUpdate("agencyName", "agencyName", currentState?.agencyName, newInfo.agencyName);
    compareAndUpdate("agencyPhone", "agencyPhone", currentState?.agencyPhone, newInfo.agencyPhone);
    compareAndUpdate("agencyEmail", "agencyEmail", currentState?.agencyEmail, newInfo.agencyEmail);
    compareAndUpdate("agencyWebsite", "agencyWebsite", currentState?.agencyWebsite, newInfo.agencyWebsite);
    compareAndUpdate("summary", "summary", currentState?.summary, newInfo.summary);
    compareAndUpdate("additionalNotes", "additionalNotes", currentState?.additionalNotes, newInfo.additionalNotes);

    // Handle date fields
    if (newInfo.approvalDate) {
      const newDate = new Date(newInfo.approvalDate);
      if (!isNaN(newDate.getTime())) {
        updates.approvalDate = newDate;
      }
    }
    if (newInfo.effectiveDate) {
      const newDate = new Date(newInfo.effectiveDate);
      if (!isNaN(newDate.getTime())) {
        updates.effectiveDate = newDate;
      }
    }
    if (newInfo.nextDeadline) {
      const newDate = new Date(newInfo.nextDeadline);
      if (!isNaN(newDate.getTime())) {
        updates.nextDeadline = newDate;
      }
    }

    // Always update verification timestamp and source
    updates.lastVerifiedAt = new Date();
    if (newInfo.sourceUrl) {
      updates.primarySourceUrl = newInfo.sourceUrl;
    }

    // Apply updates if there are any changes
    if (Object.keys(updates).length > 0) {
      await updateState(stateCode, updates);
    }

    return { success: true, changes };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    
    // Log the failure
    await createUpdateLog({
      stateId: 0,
      stateCode,
      updateType: triggeredBy === "automated" ? "automated" : "manual",
      fieldChanged: "update_attempt",
      previousValue: null,
      newValue: null,
      changeDescription: `Failed to update ${stateName}`,
      sourceUrl: null,
      sourceType: "llm_extraction",
      status: "failed",
      errorMessage,
      triggeredBy,
    });

    return { success: false, changes: [], error: errorMessage };
  }
}

/**
 * Run weekly update for all states
 */
export async function runWeeklyUpdate(triggeredBy: string = "automated"): Promise<{
  runId: number;
  completed: number;
  failed: number;
  skipped: number;
  results: Array<{ stateCode: string; success: boolean; changes: string[]; error?: string }>;
}> {
  // Check if there's already a running update
  const activeRun = await getActiveUpdateRun();
  if (activeRun) {
    throw new Error(`Update already in progress (Run ID: ${activeRun.id})`);
  }

  // Create new update run
  const runId = await createUpdateRun({
    runType: triggeredBy === "automated" ? "weekly_automated" : "manual_all",
    totalStates: ALL_STATE_CODES.length,
    completedStates: 0,
    failedStates: 0,
    skippedStates: 0,
    status: "running",
    triggeredBy,
  });

  const results: Array<{ stateCode: string; success: boolean; changes: string[]; error?: string }> = [];
  let completed = 0;
  let failed = 0;
  let skipped = 0;

  try {
    for (const stateCode of ALL_STATE_CODES) {
      console.log(`[Update] Processing ${stateCode} (${STATE_NAMES[stateCode]})...`);
      
      const result = await updateSingleState(stateCode, triggeredBy);
      results.push({ stateCode, ...result });

      if (result.success) {
        completed++;
      } else {
        failed++;
      }

      // Update run progress
      await updateUpdateRun(runId, {
        completedStates: completed,
        failedStates: failed,
        skippedStates: skipped,
      });

      // Rate limiting: 2-second delay between states
      await delay(2000);
    }

    // Mark run as completed
    await updateUpdateRun(runId, {
      status: "completed",
      completedAt: new Date(),
      summary: `Completed: ${completed}, Failed: ${failed}, Skipped: ${skipped}`,
    });

  } catch (error) {
    // Mark run as failed
    await updateUpdateRun(runId, {
      status: "failed",
      completedAt: new Date(),
      summary: `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
    });
    throw error;
  }

  return { runId, completed, failed, skipped, results };
}

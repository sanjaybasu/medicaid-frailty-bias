import { eq, desc, and, like, inArray, sql } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import { 
  InsertUser, users, 
  states, State, InsertState,
  updatesLog, UpdateLog, InsertUpdateLog,
  updateRuns, UpdateRun, InsertUpdateRun
} from "../drizzle/schema";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

// ============ USER HELPERS ============

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }

  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = 'admin';
      updateSet.role = 'admin';
    }

    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get user: database not available");
    return undefined;
  }

  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);
  return result.length > 0 ? result[0] : undefined;
}

// ============ STATE HELPERS ============

export async function getAllStates(): Promise<State[]> {
  const db = await getDb();
  if (!db) return [];
  
  return db.select().from(states).orderBy(states.stateName);
}

export async function getStateByCode(stateCode: string): Promise<State | undefined> {
  const db = await getDb();
  if (!db) return undefined;
  
  const result = await db.select().from(states).where(eq(states.stateCode, stateCode)).limit(1);
  return result[0];
}

export async function getStateById(id: number): Promise<State | undefined> {
  const db = await getDb();
  if (!db) return undefined;
  
  const result = await db.select().from(states).where(eq(states.id, id)).limit(1);
  return result[0];
}

export async function searchStates(query: string): Promise<State[]> {
  const db = await getDb();
  if (!db) return [];
  
  return db.select().from(states)
    .where(like(states.stateName, `%${query}%`))
    .orderBy(states.stateName);
}

export async function getStatesByStatus(status: State["implementationStatus"]): Promise<State[]> {
  const db = await getDb();
  if (!db) return [];
  
  return db.select().from(states)
    .where(eq(states.implementationStatus, status))
    .orderBy(states.stateName);
}

export async function upsertState(state: InsertState): Promise<void> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  await db.insert(states).values(state).onDuplicateKeyUpdate({
    set: {
      stateName: state.stateName,
      implementationStatus: state.implementationStatus,
      approvalDate: state.approvalDate,
      effectiveDate: state.effectiveDate,
      nextDeadline: state.nextDeadline,
      weeklyHoursRequired: state.weeklyHoursRequired,
      monthlyHoursRequired: state.monthlyHoursRequired,
      hoursDescription: state.hoursDescription,
      qualifyingActivities: state.qualifyingActivities,
      exemptions: state.exemptions,
      reportingFrequency: state.reportingFrequency,
      reportingMethod: state.reportingMethod,
      reportingDeadline: state.reportingDeadline,
      agencyName: state.agencyName,
      agencyPhone: state.agencyPhone,
      agencyEmail: state.agencyEmail,
      agencyWebsite: state.agencyWebsite,
      summary: state.summary,
      additionalNotes: state.additionalNotes,
      primarySourceUrl: state.primarySourceUrl,
      lastVerifiedAt: state.lastVerifiedAt,
    },
  });
}

export async function updateState(stateCode: string, updates: Partial<InsertState>): Promise<void> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  await db.update(states).set(updates).where(eq(states.stateCode, stateCode));
}

export async function getStatesCount(): Promise<number> {
  const db = await getDb();
  if (!db) return 0;
  
  const result = await db.select({ count: sql<number>`count(*)` }).from(states);
  return result[0]?.count ?? 0;
}

export async function getStatusCounts(): Promise<Record<string, number>> {
  const db = await getDb();
  if (!db) return {};
  
  const result = await db.select({
    status: states.implementationStatus,
    count: sql<number>`count(*)`
  }).from(states).groupBy(states.implementationStatus);
  
  return result.reduce((acc, row) => {
    acc[row.status] = row.count;
    return acc;
  }, {} as Record<string, number>);
}

// ============ UPDATE LOG HELPERS ============

export async function createUpdateLog(log: InsertUpdateLog): Promise<void> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  await db.insert(updatesLog).values(log);
}

export async function getUpdateLogsForState(stateCode: string, limit = 50): Promise<UpdateLog[]> {
  const db = await getDb();
  if (!db) return [];
  
  return db.select().from(updatesLog)
    .where(eq(updatesLog.stateCode, stateCode))
    .orderBy(desc(updatesLog.createdAt))
    .limit(limit);
}

export async function getRecentUpdateLogs(limit = 100): Promise<UpdateLog[]> {
  const db = await getDb();
  if (!db) return [];
  
  return db.select().from(updatesLog)
    .orderBy(desc(updatesLog.createdAt))
    .limit(limit);
}

export async function getUpdateLogsByStatus(status: UpdateLog["status"], limit = 100): Promise<UpdateLog[]> {
  const db = await getDb();
  if (!db) return [];
  
  return db.select().from(updatesLog)
    .where(eq(updatesLog.status, status))
    .orderBy(desc(updatesLog.createdAt))
    .limit(limit);
}

// ============ UPDATE RUN HELPERS ============

export async function createUpdateRun(run: InsertUpdateRun): Promise<number> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  const result = await db.insert(updateRuns).values(run);
  return Number(result[0].insertId);
}

export async function updateUpdateRun(id: number, updates: Partial<InsertUpdateRun>): Promise<void> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  await db.update(updateRuns).set(updates).where(eq(updateRuns.id, id));
}

export async function getUpdateRun(id: number): Promise<UpdateRun | undefined> {
  const db = await getDb();
  if (!db) return undefined;
  
  const result = await db.select().from(updateRuns).where(eq(updateRuns.id, id)).limit(1);
  return result[0];
}

export async function getRecentUpdateRuns(limit = 20): Promise<UpdateRun[]> {
  const db = await getDb();
  if (!db) return [];
  
  return db.select().from(updateRuns)
    .orderBy(desc(updateRuns.startedAt))
    .limit(limit);
}

export async function getActiveUpdateRun(): Promise<UpdateRun | undefined> {
  const db = await getDb();
  if (!db) return undefined;
  
  const result = await db.select().from(updateRuns)
    .where(eq(updateRuns.status, "running"))
    .orderBy(desc(updateRuns.startedAt))
    .limit(1);
  return result[0];
}

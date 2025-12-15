import { int, mysqlEnum, mysqlTable, text, timestamp, varchar, json, boolean } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 */
export const users = mysqlTable("users", {
  id: int("id").autoincrement().primaryKey(),
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

/**
 * States table storing Medicaid work requirement information for all 50 states + DC
 */
export const states = mysqlTable("states", {
  id: int("id").autoincrement().primaryKey(),
  /** State abbreviation (e.g., "AL", "CA", "DC") */
  stateCode: varchar("stateCode", { length: 2 }).notNull().unique(),
  /** Full state name */
  stateName: varchar("stateName", { length: 100 }).notNull(),
  
  /** Implementation status */
  implementationStatus: mysqlEnum("implementationStatus", [
    "not_implemented",
    "pending_approval", 
    "approved_not_active",
    "active",
    "suspended",
    "terminated"
  ]).default("not_implemented").notNull(),
  
  /** Key dates */
  approvalDate: timestamp("approvalDate"),
  effectiveDate: timestamp("effectiveDate"),
  nextDeadline: timestamp("nextDeadline"),
  
  /** Work hour requirements */
  weeklyHoursRequired: int("weeklyHoursRequired"),
  monthlyHoursRequired: int("monthlyHoursRequired"),
  hoursDescription: text("hoursDescription"),
  
  /** Qualifying activities (stored as JSON array) */
  qualifyingActivities: json("qualifyingActivities").$type<string[]>(),
  
  /** Exemptions (stored as JSON array) */
  exemptions: json("exemptions").$type<string[]>(),
  
  /** Reporting requirements */
  reportingFrequency: varchar("reportingFrequency", { length: 50 }),
  reportingMethod: text("reportingMethod"),
  reportingDeadline: text("reportingDeadline"),
  
  /** Contact information */
  agencyName: varchar("agencyName", { length: 255 }),
  agencyPhone: varchar("agencyPhone", { length: 50 }),
  agencyEmail: varchar("agencyEmail", { length: 255 }),
  agencyWebsite: text("agencyWebsite"),
  
  /** Additional information */
  summary: text("summary"),
  additionalNotes: text("additionalNotes"),
  
  /** Source tracking */
  primarySourceUrl: text("primarySourceUrl"),
  lastVerifiedAt: timestamp("lastVerifiedAt"),
  
  /** Timestamps */
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type State = typeof states.$inferSelect;
export type InsertState = typeof states.$inferInsert;

/**
 * Update logs table for tracking all changes with full audit trail
 */
export const updatesLog = mysqlTable("updates_log", {
  id: int("id").autoincrement().primaryKey(),
  
  /** Reference to the state */
  stateId: int("stateId").notNull(),
  stateCode: varchar("stateCode", { length: 2 }).notNull(),
  
  /** Update metadata */
  updateType: mysqlEnum("updateType", [
    "automated",
    "manual",
    "initial_seed"
  ]).default("automated").notNull(),
  
  /** What changed */
  fieldChanged: varchar("fieldChanged", { length: 100 }).notNull(),
  previousValue: text("previousValue"),
  newValue: text("newValue"),
  changeDescription: text("changeDescription"),
  
  /** Source information */
  sourceUrl: text("sourceUrl"),
  sourceType: varchar("sourceType", { length: 50 }),
  
  /** Status */
  status: mysqlEnum("status", [
    "success",
    "failed",
    "pending",
    "skipped"
  ]).default("success").notNull(),
  errorMessage: text("errorMessage"),
  
  /** Who made the change */
  triggeredBy: varchar("triggeredBy", { length: 100 }),
  
  /** Timestamps */
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type UpdateLog = typeof updatesLog.$inferSelect;
export type InsertUpdateLog = typeof updatesLog.$inferInsert;

/**
 * Update runs table for tracking batch update operations
 */
export const updateRuns = mysqlTable("update_runs", {
  id: int("id").autoincrement().primaryKey(),
  
  /** Run metadata */
  runType: mysqlEnum("runType", [
    "weekly_automated",
    "manual_all",
    "manual_single"
  ]).default("weekly_automated").notNull(),
  
  /** Progress tracking */
  totalStates: int("totalStates").default(51).notNull(),
  completedStates: int("completedStates").default(0).notNull(),
  failedStates: int("failedStates").default(0).notNull(),
  skippedStates: int("skippedStates").default(0).notNull(),
  
  /** Status */
  status: mysqlEnum("status", [
    "running",
    "completed",
    "failed",
    "cancelled"
  ]).default("running").notNull(),
  
  /** Timing */
  startedAt: timestamp("startedAt").defaultNow().notNull(),
  completedAt: timestamp("completedAt"),
  
  /** Who triggered */
  triggeredBy: varchar("triggeredBy", { length: 100 }),
  
  /** Summary */
  summary: text("summary"),
});

export type UpdateRun = typeof updateRuns.$inferSelect;
export type InsertUpdateRun = typeof updateRuns.$inferInsert;

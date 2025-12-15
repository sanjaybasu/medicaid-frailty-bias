import { COOKIE_NAME } from "@shared/const";
import { TRPCError } from "@trpc/server";
import { z } from "zod";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, protectedProcedure, router } from "./_core/trpc";
import {
  getAllStates,
  getStateByCode,
  searchStates,
  getStatesByStatus,
  getStatesCount,
  getStatusCounts,
  getUpdateLogsForState,
  getRecentUpdateLogs,
  getUpdateLogsByStatus,
  getRecentUpdateRuns,
  getActiveUpdateRun,
  getUpdateRun,
  updateState,
} from "./db";
import { updateSingleState, runWeeklyUpdate, ALL_STATE_CODES, STATE_NAMES } from "./updateService";
import { seedAllStates } from "./seedStates";

// Admin-only procedure
const adminProcedure = protectedProcedure.use(({ ctx, next }) => {
  if (ctx.user.role !== "admin") {
    throw new TRPCError({ code: "FORBIDDEN", message: "Admin access required" });
  }
  return next({ ctx });
});

export const appRouter = router({
  system: systemRouter,
  
  auth: router({
    me: publicProcedure.query((opts) => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),

  // Public state data endpoints
  states: router({
    // Get all states with their current status
    list: publicProcedure.query(async () => {
      return getAllStates();
    }),

    // Get a single state by code
    byCode: publicProcedure
      .input(z.object({ code: z.string().length(2) }))
      .query(async ({ input }) => {
        const state = await getStateByCode(input.code.toUpperCase());
        if (!state) {
          throw new TRPCError({ code: "NOT_FOUND", message: "State not found" });
        }
        return state;
      }),

    // Search states by name
    search: publicProcedure
      .input(z.object({ query: z.string() }))
      .query(async ({ input }) => {
        return searchStates(input.query);
      }),

    // Filter states by implementation status
    byStatus: publicProcedure
      .input(z.object({ 
        status: z.enum([
          "not_implemented",
          "pending_approval",
          "approved_not_active",
          "active",
          "suspended",
          "terminated"
        ])
      }))
      .query(async ({ input }) => {
        return getStatesByStatus(input.status);
      }),

    // Get dashboard statistics
    stats: publicProcedure.query(async () => {
      const [totalCount, statusCounts] = await Promise.all([
        getStatesCount(),
        getStatusCounts(),
      ]);
      return { totalCount, statusCounts };
    }),

    // Get update history for a state
    updates: publicProcedure
      .input(z.object({ code: z.string().length(2), limit: z.number().optional() }))
      .query(async ({ input }) => {
        return getUpdateLogsForState(input.code.toUpperCase(), input.limit);
      }),

    // Get all state codes and names (for dropdowns, etc.)
    codes: publicProcedure.query(() => {
      return ALL_STATE_CODES.map((code) => ({
        code,
        name: STATE_NAMES[code],
      }));
    }),
  }),

  // Admin endpoints
  admin: router({
    // Get recent update logs
    recentLogs: adminProcedure
      .input(z.object({ limit: z.number().optional() }))
      .query(async ({ input }) => {
        return getRecentUpdateLogs(input.limit);
      }),

    // Get logs by status
    logsByStatus: adminProcedure
      .input(z.object({ 
        status: z.enum(["success", "failed", "pending", "skipped"]),
        limit: z.number().optional()
      }))
      .query(async ({ input }) => {
        return getUpdateLogsByStatus(input.status, input.limit);
      }),

    // Get update runs history
    updateRuns: adminProcedure
      .input(z.object({ limit: z.number().optional() }))
      .query(async ({ input }) => {
        return getRecentUpdateRuns(input.limit);
      }),

    // Get active update run
    activeRun: adminProcedure.query(async () => {
      return getActiveUpdateRun();
    }),

    // Get specific update run
    updateRun: adminProcedure
      .input(z.object({ id: z.number() }))
      .query(async ({ input }) => {
        return getUpdateRun(input.id);
      }),

    // Trigger update for a single state
    updateState: adminProcedure
      .input(z.object({ code: z.string().length(2) }))
      .mutation(async ({ input, ctx }) => {
        const result = await updateSingleState(
          input.code.toUpperCase(),
          ctx.user.name || ctx.user.email || "admin"
        );
        return result;
      }),

    // Trigger update for all states
    updateAllStates: adminProcedure.mutation(async ({ ctx }) => {
      const result = await runWeeklyUpdate(
        ctx.user.name || ctx.user.email || "admin"
      );
      return result;
    }),

    // Seed initial state data
    seedStates: adminProcedure.mutation(async () => {
      await seedAllStates();
      return { success: true, message: "All states seeded successfully" };
    }),

    // Manually update state information
    editState: adminProcedure
      .input(z.object({
        code: z.string().length(2),
        updates: z.object({
          implementationStatus: z.enum([
            "not_implemented",
            "pending_approval",
            "approved_not_active",
            "active",
            "suspended",
            "terminated"
          ]).optional(),
          weeklyHoursRequired: z.number().nullable().optional(),
          monthlyHoursRequired: z.number().nullable().optional(),
          hoursDescription: z.string().nullable().optional(),
          qualifyingActivities: z.array(z.string()).nullable().optional(),
          exemptions: z.array(z.string()).nullable().optional(),
          reportingFrequency: z.string().nullable().optional(),
          reportingMethod: z.string().nullable().optional(),
          reportingDeadline: z.string().nullable().optional(),
          agencyName: z.string().nullable().optional(),
          agencyPhone: z.string().nullable().optional(),
          agencyEmail: z.string().nullable().optional(),
          agencyWebsite: z.string().nullable().optional(),
          summary: z.string().nullable().optional(),
          additionalNotes: z.string().nullable().optional(),
          primarySourceUrl: z.string().nullable().optional(),
        }),
      }))
      .mutation(async ({ input }) => {
        await updateState(input.code.toUpperCase(), input.updates);
        return { success: true };
      }),

    // Dashboard stats for admin
    dashboardStats: adminProcedure.query(async () => {
      const [states, statusCounts, recentLogs, activeRun, recentRuns] = await Promise.all([
        getAllStates(),
        getStatusCounts(),
        getRecentUpdateLogs(10),
        getActiveUpdateRun(),
        getRecentUpdateRuns(5),
      ]);

      const lastUpdated = states.reduce((latest, state) => {
        if (!latest || (state.updatedAt && state.updatedAt > latest)) {
          return state.updatedAt;
        }
        return latest;
      }, null as Date | null);

      return {
        totalStates: states.length,
        statusCounts,
        recentLogs,
        activeRun,
        recentRuns,
        lastUpdated,
      };
    }),
  }),
});

export type AppRouter = typeof appRouter;

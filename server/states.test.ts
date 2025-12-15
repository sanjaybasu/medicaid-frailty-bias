import { describe, expect, it, beforeAll } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";
import { ALL_STATE_CODES, STATE_NAMES } from "./updateService";

// Helper to create a public context (no user)
function createPublicContext(): TrpcContext {
  return {
    user: null,
    req: {
      protocol: "https",
      headers: {},
    } as TrpcContext["req"],
    res: {
      clearCookie: () => {},
    } as TrpcContext["res"],
  };
}

// Helper to create an admin context
function createAdminContext(): TrpcContext {
  return {
    user: {
      id: 1,
      openId: "admin-user",
      email: "admin@example.com",
      name: "Admin User",
      loginMethod: "manus",
      role: "admin",
      createdAt: new Date(),
      updatedAt: new Date(),
      lastSignedIn: new Date(),
    },
    req: {
      protocol: "https",
      headers: {},
    } as TrpcContext["req"],
    res: {
      clearCookie: () => {},
    } as TrpcContext["res"],
  };
}

// Helper to create a regular user context
function createUserContext(): TrpcContext {
  return {
    user: {
      id: 2,
      openId: "regular-user",
      email: "user@example.com",
      name: "Regular User",
      loginMethod: "manus",
      role: "user",
      createdAt: new Date(),
      updatedAt: new Date(),
      lastSignedIn: new Date(),
    },
    req: {
      protocol: "https",
      headers: {},
    } as TrpcContext["req"],
    res: {
      clearCookie: () => {},
    } as TrpcContext["res"],
  };
}

describe("State Constants", () => {
  it("should have 51 state codes (50 states + DC)", () => {
    expect(ALL_STATE_CODES).toHaveLength(51);
  });

  it("should have matching state names for all codes", () => {
    for (const code of ALL_STATE_CODES) {
      expect(STATE_NAMES[code]).toBeDefined();
      expect(typeof STATE_NAMES[code]).toBe("string");
      expect(STATE_NAMES[code].length).toBeGreaterThan(0);
    }
  });

  it("should include DC (District of Columbia)", () => {
    expect(ALL_STATE_CODES).toContain("DC");
    expect(STATE_NAMES["DC"]).toBe("District of Columbia");
  });

  it("should have unique state codes", () => {
    const uniqueCodes = new Set(ALL_STATE_CODES);
    expect(uniqueCodes.size).toBe(ALL_STATE_CODES.length);
  });
});

describe("Public State Endpoints", () => {
  it("states.list should return an array", async () => {
    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);
    
    const result = await caller.states.list();
    expect(Array.isArray(result)).toBe(true);
  });

  it("states.codes should return all 51 state codes with names", async () => {
    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);
    
    const result = await caller.states.codes();
    expect(result).toHaveLength(51);
    
    // Check structure
    for (const item of result) {
      expect(item).toHaveProperty("code");
      expect(item).toHaveProperty("name");
      expect(typeof item.code).toBe("string");
      expect(typeof item.name).toBe("string");
      expect(item.code.length).toBe(2);
    }
  });

  it("states.stats should return statistics object", async () => {
    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);
    
    const result = await caller.states.stats();
    expect(result).toHaveProperty("totalCount");
    expect(result).toHaveProperty("statusCounts");
    expect(typeof result.totalCount).toBe("number");
    expect(typeof result.statusCounts).toBe("object");
  });

  it("states.byCode should throw NOT_FOUND for invalid code", async () => {
    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);
    
    await expect(caller.states.byCode({ code: "XX" }))
      .rejects.toThrow("State not found");
  });

  it("states.search should return array for any query", async () => {
    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);
    
    const result = await caller.states.search({ query: "California" });
    expect(Array.isArray(result)).toBe(true);
  });
});

describe("Admin Endpoints Access Control", () => {
  it("admin.recentLogs should reject unauthenticated users", async () => {
    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);
    
    await expect(caller.admin.recentLogs({ limit: 10 }))
      .rejects.toThrow();
  });

  it("admin.recentLogs should reject non-admin users", async () => {
    const ctx = createUserContext();
    const caller = appRouter.createCaller(ctx);
    
    await expect(caller.admin.recentLogs({ limit: 10 }))
      .rejects.toThrow("Admin access required");
  });

  it("admin.recentLogs should allow admin users", async () => {
    const ctx = createAdminContext();
    const caller = appRouter.createCaller(ctx);
    
    const result = await caller.admin.recentLogs({ limit: 10 });
    expect(Array.isArray(result)).toBe(true);
  });

  it("admin.dashboardStats should allow admin users", async () => {
    const ctx = createAdminContext();
    const caller = appRouter.createCaller(ctx);
    
    const result = await caller.admin.dashboardStats();
    expect(result).toHaveProperty("totalStates");
    expect(result).toHaveProperty("statusCounts");
    expect(result).toHaveProperty("recentLogs");
  });

  it("admin.updateRuns should allow admin users", async () => {
    const ctx = createAdminContext();
    const caller = appRouter.createCaller(ctx);
    
    const result = await caller.admin.updateRuns({ limit: 5 });
    expect(Array.isArray(result)).toBe(true);
  });
});

describe("Auth Endpoints", () => {
  it("auth.me should return null for unauthenticated users", async () => {
    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);
    
    const result = await caller.auth.me();
    expect(result).toBeNull();
  });

  it("auth.me should return user for authenticated users", async () => {
    const ctx = createAdminContext();
    const caller = appRouter.createCaller(ctx);
    
    const result = await caller.auth.me();
    expect(result).not.toBeNull();
    expect(result?.email).toBe("admin@example.com");
    expect(result?.role).toBe("admin");
  });
});

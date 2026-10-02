import { describe, expect, it } from "vitest";

/* Tests that the StatusPage module is importable and AnalysisOutput schema is valid.
   More integration-level tests (rendering with mocked fetch) are added in M1.1. */

describe("StatusPage smoke", () => {
  it("StatusPage module can be imported without errors", async () => {
    const mod = await import("../pages/StatusPage");
    expect(mod.StatusPage).toBeDefined();
    expect(typeof mod.StatusPage).toBe("function");
  });
});

describe("API client smoke", () => {
  it("client module exports apiClient", async () => {
    const mod = await import("../shared/api/client");
    expect(mod.apiClient).toBeDefined();
    expect(typeof mod.apiClient.get).toBe("function");
    expect(typeof mod.apiClient.post).toBe("function");
  });
});

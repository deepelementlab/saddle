import { describe, expect, it } from "vitest";
import { defaultCollaborationConfig, normalizeStageCollaboration, newPrimitiveId } from "./collaboration";

describe("newPrimitiveId", () => {
  it("returns a string containing the prefix", () => {
    const id = newPrimitiveId("test");
    expect(id).toContain("test-");
    expect(id.length).toBeGreaterThan(8);
  });
});

describe("normalizeStageCollaboration", () => {
  it("migrates legacy operation_primitives for design", () => {
    const raw = {
      collaboration_format: { team: "designteam", mode: "custom" },
      operation_primitives: ["step_a", "step_b"],
    };
    const out = normalizeStageCollaboration("design", raw);
    expect(out.primitives.map((p) => p.key)).toEqual(["step_a", "step_b"]);
    expect(out.groups.length).toBeGreaterThan(0);
    expect(out.collaboration_format.team).toBe("designteam");
    expect(out.collaboration_format.mode).toBe("custom");
  });

  it("returns defaults for empty input", () => {
    const out = normalizeStageCollaboration("develop", null);
    expect(out.primitives.length).toBeGreaterThan(0);
    expect(out.groups.length).toBeGreaterThan(0);
  });
});

describe("defaultCollaborationConfig", () => {
  it("has design and develop with primitives", () => {
    const c = defaultCollaborationConfig();
    expect(c.design.primitives.length).toBeGreaterThan(0);
    expect(c.develop.primitives.length).toBeGreaterThan(0);
  });
});

import type { CollaborationPrimitive, PrimitiveGroupDef, StageCollaboration } from "../types/collaboration";

const emptyObjectSchema = (): Record<string, unknown> => ({
  type: "object",
  additionalProperties: true,
  properties: {},
});

export function newPrimitiveId(prefix: string): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return `${prefix}-${crypto.randomUUID()}`;
  }
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function migrateStringPrimitives(
  format: Record<string, string>,
  keys: string[],
  groupByIndex: (i: number) => string | null
): StageCollaboration {
  const primitives: CollaborationPrimitive[] = keys.map((key, i) => ({
    id: newPrimitiveId(key),
    key,
    label: key.replace(/_/g, " "),
    group_id: groupByIndex(i),
    constraints: [],
    input_schema: emptyObjectSchema(),
    output_schema: emptyObjectSchema(),
  }));
  return {
    collaboration_format: { ...format },
    groups: [],
    primitives,
  };
}

function ensurePrimitiveShape(p: unknown, prefix: string): CollaborationPrimitive | null {
  if (!p || typeof p !== "object") return null;
  const o = p as Record<string, unknown>;
  const key = typeof o.key === "string" ? o.key : "";
  if (!key) return null;
  const id = typeof o.id === "string" ? o.id : newPrimitiveId(prefix);
  const label = typeof o.label === "string" ? o.label : key;
  const group_id =
    o.group_id === null || o.group_id === undefined
      ? null
      : typeof o.group_id === "string"
        ? o.group_id
        : null;
  const constraints = Array.isArray(o.constraints)
    ? (o.constraints as unknown[]).map((x) => String(x)).filter(Boolean)
    : [];
  const input_schema =
    o.input_schema && typeof o.input_schema === "object" && !Array.isArray(o.input_schema)
      ? (o.input_schema as Record<string, unknown>)
      : emptyObjectSchema();
  const output_schema =
    o.output_schema && typeof o.output_schema === "object" && !Array.isArray(o.output_schema)
      ? (o.output_schema as Record<string, unknown>)
      : emptyObjectSchema();
  return { id, key, label, group_id, constraints, input_schema, output_schema };
}

function normalizeGroups(raw: unknown): PrimitiveGroupDef[] {
  if (!Array.isArray(raw)) return [];
  const out: PrimitiveGroupDef[] = [];
  for (const g of raw) {
    if (!g || typeof g !== "object") continue;
    const o = g as Record<string, unknown>;
    const id = typeof o.id === "string" ? o.id : "";
    if (!id) continue;
    const label = typeof o.label === "string" ? o.label : id;
    const order = typeof o.order === "number" ? o.order : out.length;
    out.push({ id, label, order });
  }
  return out.sort((a, b) => a.order - b.order);
}

export function normalizeStageCollaboration(stage: string, raw: unknown): StageCollaboration {
  const base = raw && typeof raw === "object" ? (raw as Record<string, unknown>) : {};
  const fmt =
    base.collaboration_format && typeof base.collaboration_format === "object" && !Array.isArray(base.collaboration_format)
      ? { ...(base.collaboration_format as Record<string, string>) }
      : {};

  const groups = normalizeGroups(base.groups);

  const primRaw = base.primitives;
  if (Array.isArray(primRaw) && primRaw.length > 0 && typeof primRaw[0] === "object") {
    const primitives = primRaw
      .map((p) => ensurePrimitiveShape(p, stage))
      .filter((x): x is CollaborationPrimitive => x !== null);
    const groupsOut =
      primitives.length > 0 && groups.length === 0
        ? defaultStageCollaboration(stage === "develop" ? "develop" : "design").groups
        : groups;
    return {
      collaboration_format: fmt,
      groups: groupsOut,
      primitives,
    };
  }

  const ops = base.operation_primitives;
  if (Array.isArray(ops) && ops.length > 0 && typeof ops[0] === "string") {
    const keys = ops as string[];
    if (stage === "design") {
      const gid = (i: number): string | null => {
        if (i <= 1) return "design-research";
        if (i <= 4) return "design-ux";
        return "design-review";
      };
      const migrated = migrateStringPrimitives(fmt, keys, gid);
      return { ...migrated, groups: defaultStageCollaboration("design").groups };
    }
    const gid = (i: number): string | null => {
      if (i <= 2) return "dev-planning";
      if (i <= 4) return "dev-execution";
      return "dev-quality";
    };
    const migrated = migrateStringPrimitives(fmt, keys, gid);
    return { ...migrated, groups: defaultStageCollaboration("develop").groups };
  }

  return defaultStageCollaboration(stage);
}

export function defaultStageCollaboration(stage: "design" | "develop"): StageCollaboration {
  if (stage === "design") {
    const groups: PrimitiveGroupDef[] = [
      { id: "design-research", label: "Research & Alignment", order: 0 },
      { id: "design-ux", label: "UX & Information Architecture", order: 1 },
      { id: "design-review", label: "Review & Handoff", order: 2 },
    ];
    const primitives: CollaborationPrimitive[] = [
      {
        id: newPrimitiveId("clarify_requirement"),
        key: "clarify_requirement",
        label: "Clarify requirement",
        group_id: "design-research",
        constraints: ["Must capture user goals and non-goals"],
        input_schema: emptyObjectSchema(),
        output_schema: emptyObjectSchema(),
      },
      {
        id: newPrimitiveId("research_context"),
        key: "research_context",
        label: "Research context",
        group_id: "design-research",
        constraints: ["Cite assumptions and unknowns explicitly"],
        input_schema: emptyObjectSchema(),
        output_schema: emptyObjectSchema(),
      },
      {
        id: newPrimitiveId("define_persona_journey"),
        key: "define_persona_journey",
        label: "Define persona journey",
        group_id: "design-ux",
        constraints: [],
        input_schema: emptyObjectSchema(),
        output_schema: emptyObjectSchema(),
      },
      {
        id: newPrimitiveId("draft_interaction_flow"),
        key: "draft_interaction_flow",
        label: "Draft interaction flow",
        group_id: "design-ux",
        constraints: [],
        input_schema: emptyObjectSchema(),
        output_schema: emptyObjectSchema(),
      },
      {
        id: newPrimitiveId("propose_ui_structure"),
        key: "propose_ui_structure",
        label: "Propose UI structure",
        group_id: "design-ux",
        constraints: [],
        input_schema: emptyObjectSchema(),
        output_schema: emptyObjectSchema(),
      },
      {
        id: newPrimitiveId("cross_role_review"),
        key: "cross_role_review",
        label: "Cross-role review",
        group_id: "design-review",
        constraints: ["At least two roles must sign off"],
        input_schema: emptyObjectSchema(),
        output_schema: emptyObjectSchema(),
      },
      {
        id: newPrimitiveId("design_handoff"),
        key: "design_handoff",
        label: "Design handoff",
        group_id: "design-review",
        constraints: ["Produce handoff artifact for develop"],
        input_schema: emptyObjectSchema(),
        output_schema: emptyObjectSchema(),
      },
    ];
    return {
      collaboration_format: {
        team: "designteam",
        mode: "multi-role orchestration",
        default_output: "design documentation and specs",
        handoff: "implementation handoff to develop",
      },
      groups,
      primitives,
    };
  }

  const groups: PrimitiveGroupDef[] = [
    { id: "dev-planning", label: "Planning & Architecture", order: 0 },
    { id: "dev-execution", label: "Execution", order: 1 },
    { id: "dev-quality", label: "Quality & Release", order: 2 },
  ];
  const primitives: CollaborationPrimitive[] = [
    {
      id: newPrimitiveId("scope_decomposition"),
      key: "scope_decomposition",
      label: "Scope decomposition",
      group_id: "dev-planning",
      constraints: [],
      input_schema: emptyObjectSchema(),
      output_schema: emptyObjectSchema(),
    },
    {
      id: newPrimitiveId("architecture_tradeoff"),
      key: "architecture_tradeoff",
      label: "Architecture tradeoff",
      group_id: "dev-planning",
      constraints: ["Document trade-offs and risks"],
      input_schema: emptyObjectSchema(),
      output_schema: emptyObjectSchema(),
    },
    {
      id: newPrimitiveId("task_scheduling"),
      key: "task_scheduling",
      label: "Task scheduling",
      group_id: "dev-planning",
      constraints: [],
      input_schema: emptyObjectSchema(),
      output_schema: emptyObjectSchema(),
    },
    {
      id: newPrimitiveId("implementation_execution"),
      key: "implementation_execution",
      label: "Implementation execution",
      group_id: "dev-execution",
      constraints: [],
      input_schema: emptyObjectSchema(),
      output_schema: emptyObjectSchema(),
    },
    {
      id: newPrimitiveId("quality_validation"),
      key: "quality_validation",
      label: "Quality validation",
      group_id: "dev-quality",
      constraints: [],
      input_schema: emptyObjectSchema(),
      output_schema: emptyObjectSchema(),
    },
    {
      id: newPrimitiveId("risk_mitigation"),
      key: "risk_mitigation",
      label: "Risk mitigation",
      group_id: "dev-quality",
      constraints: [],
      input_schema: emptyObjectSchema(),
      output_schema: emptyObjectSchema(),
    },
    {
      id: newPrimitiveId("release_readiness"),
      key: "release_readiness",
      label: "Release readiness",
      group_id: "dev-quality",
      constraints: ["Exit criteria must be explicit"],
      input_schema: emptyObjectSchema(),
      output_schema: emptyObjectSchema(),
    },
  ];
  return {
    collaboration_format: {
      team: "clawteam",
      mode: "engineering multi-role orchestration",
      default_output: "implementation plan and execution-ready prompt",
      handoff: "delivery and QA closure",
    },
    groups,
    primitives,
  };
}

export function defaultCollaborationConfig(): {
  design: StageCollaboration;
  develop: StageCollaboration;
} {
  return {
    design: defaultStageCollaboration("design"),
    develop: defaultStageCollaboration("develop"),
  };
}

/** Structured collaboration config for design/develop team stages (maps to designteam/clawteam at runtime). */

export interface PrimitiveGroupDef {
  id: string;
  label: string;
  order: number;
}

export interface CollaborationPrimitive {
  id: string;
  key: string;
  label: string;
  /** null = ungrouped */
  group_id: string | null;
  constraints: string[];
  input_schema: Record<string, unknown>;
  output_schema: Record<string, unknown>;
}

export interface StageCollaboration {
  collaboration_format: Record<string, string>;
  groups: PrimitiveGroupDef[];
  primitives: CollaborationPrimitive[];
  /** legacy: string keys only */
  operation_primitives?: string[];
}

# Saddle collaboration: `collaboration_config` reference

[中文说明](./COLLABORATION_CONFIG.zh.md)

This document describes how Saddle modes configure **intelligent collaboration**: the `collaboration_config` block, **groups**, **primitives**, the **`operation_primitives`** shorthand, and copy-paste YAML examples. Normalization and defaults are implemented in [`src/saddle/modes/collaboration_payload.py`](../src/saddle/modes/collaboration_payload.py).

---

## 1. Three layers (macro → micro)

1. **Pipeline**  
   Default order **`spec → design → develop`**, controlled by `pipeline.order` and per-stage `enabled` flags.

2. **Stage orchestration (`design` / `develop`)**  
   Per-stage knobs such as `deep_loop`, `max_iters`, and `prompt_profile` (`full` / `compact`). Together with root-level `agent_selection`, `thresholds`, `tool_policy`, `role_mindsets`, etc., they define how the team run behaves.

3. **`collaboration_config` (collaboration primitives)**  
   Applies only to the **`design`** and **`develop`** stages. It describes:
   - **Groups (`groups`)**: swimlanes (`id`, `label`, `order`);
   - **Primitives (`primitives`)**: named collaboration steps (`key` required; optional constraints and JSON Schemas);
   - **`collaboration_format`**: string key/value map **shallow-merged** over built-in defaults (team/mode/default output/handoff semantics);
   - **`operation_primitives`**: list of strings expanded into full primitives and assigned to **default groups** by index.

If **`collaboration_config` is omitted** from a mode YAML, the loader injects the code defaults (`_default_design_stage` / `_default_develop_stage`).

---

## 2. Top-level shape

```yaml
collaboration_config:
  design:
    collaboration_format: { ... }   # optional shallow merge
    groups: [ ... ]
    primitives: [ ... ]              # list of objects = full primitives
    operation_primitives: [ ... ]    # list of strings = shorthand
  develop:
    # same fields
```

**Precedence**: If **`primitives`** is a non-empty list whose first element is a **dict**, the normalizer takes the **full primitives** path and does **not** use `operation_primitives` for that stage.

---

## 3. Groups (`groups`)

Each entry is an object:

| Field | Required | Description |
|-------|------------|-------------|
| `id` | Yes | Stable group id; referenced by `primitives[].group_id` |
| `label` | No | Display label; defaults to `id` |
| `order` | No | Number used for sorting; defaults to current list length |

Built-in **design** group ids: `design-research`, `design-ux`, `design-review`.  
Built-in **develop** group ids: `dev-planning`, `dev-execution`, `dev-quality`.

---

## 4. Primitives vs `operation_primitives`

### 4.1 Full primitive object

| Field | Required | Description |
|-------|------------|-------------|
| `key` | Yes | Stable step identifier |
| `id` | No | Instance id; generated if omitted |
| `label` | No | Display label; defaults to `key` |
| `group_id` | No | Must match a `groups[].id` (or a built-in default group id) |
| `constraints` | No | List of strings (prompt/collaboration hints) |
| `input_schema` / `output_schema` | No | Must be **object-shaped** JSON Schema dicts; invalid/missing values fall back to an empty object schema with `additionalProperties: true` |

### 4.2 `primitives` without `groups`

When `primitives` is non-empty and the first item is a **dict**: if no valid `groups` are provided, the normalizer **reuses the default groups** for that stage (design triple or develop triple).

### 4.3 `operation_primitives` index → default group

When the **string-list shorthand** is used, each string becomes a primitive; **`group_id` is chosen by zero-based index**:

**Design** (index `i`):

- `i <= 1` → `design-research`
- `2 <= i <= 4` → `design-ux`
- `i >= 5` → `design-review`

**Develop**:

- `i <= 2` → `dev-planning`
- `3 <= i <= 4` → `dev-execution`
- `i >= 5` → `dev-quality`

---

## 5. `collaboration_format`

Shallow string merge over the stage’s default `collaboration_format`. Typical keys include `team`, `mode`, `default_output`, and `handoff` (see defaults in `collaboration_payload.py`).

---

## 6. Relation to bundled modes

The bundled **`.saddle/modes/default.yaml`**, **`fast.yaml`**, and **`deep.yaml`** files mostly tune pipeline, iteration limits, `agent_selection`, and `thresholds`. They usually **do not** embed `collaboration_config`. Add `collaboration_config` in your own mode file when you need custom groups or steps.

---

## 7. Examples

### Example A: Override `collaboration_format` only (defaults for groups/primitives)

```yaml
name: branded_default
pipeline:
  enabled: true
  order: [spec, design, develop]
spec:
  enabled: true
design:
  enabled: true
develop:
  enabled: true
collaboration_config:
  design:
    collaboration_format:
      team: "Product + design dual track"
      default_output: "UI/IA notes ready for develop"
  develop:
    collaboration_format:
      team: "Engineering delivery pod"
      handoff: "Pre-merge self-check complete"
```

### Example B: `operation_primitives` for design (six steps → research / ux / review)

```yaml
collaboration_config:
  design:
    collaboration_format:
      mode: "Lightweight design review"
    operation_primitives:
      - clarify_business_goal
      - list_unknowns
      - user_flow_sketch
      - screen_outline
      - data_contract_draft
      - signoff_for_dev
```

### Example C: `operation_primitives` for develop (six steps → planning / execution / quality)

```yaml
collaboration_config:
  develop:
    operation_primitives:
      - backlog_slice
      - tech_spike
      - interface_contract
      - implement_core
      - wire_tests
      - release_checklist
```

### Example D: Custom `groups` + full `primitives`

```yaml
collaboration_config:
  design:
    collaboration_format:
      team: "Security design squad"
      default_output: "Threat model and controls"
    groups:
      - { id: threat, label: "Threat modeling", order: 0 }
      - { id: controls, label: "Controls & acceptance", order: 1 }
    primitives:
      - key: asset_inventory
        label: Assets and trust boundaries
        group_id: threat
        constraints:
          - "List data stores and external dependencies"
        input_schema: { type: object, properties: {}, additionalProperties: true }
        output_schema: { type: object, properties: {}, additionalProperties: true }
      - key: control_backlog
        label: Control backlog
        group_id: controls
        constraints:
          - "Each control must be verifiable"
        input_schema: { type: object, properties: {}, additionalProperties: true }
        output_schema: { type: object, properties: {}, additionalProperties: true }
```

### Example E: Full `primitives` + built-in develop group ids (omit `groups`)

```yaml
collaboration_config:
  develop:
    collaboration_format:
      default_output: "Tested, PR-sized increments"
    primitives:
      - key: scope_decomposition
        label: Scope decomposition
        group_id: dev-planning
        constraints: ["Each slice mergeable independently"]
      - key: implementation_execution
        label: Implementation and self-test
        group_id: dev-execution
      - key: quality_validation
        label: Quality gate
        group_id: dev-quality
        constraints: ["Exit criteria explicit"]
```

### Example F: Both stages in one mode

```yaml
name: collab_explicit
pipeline:
  enabled: true
  order: [spec, design, develop]
design:
  enabled: true
develop:
  enabled: true
collaboration_config:
  design:
    groups:
      - { id: design-research, label: "Alignment", order: 0 }
      - { id: design-ux, label: "Solution", order: 1 }
    primitives:
      - { key: clarify_requirement, label: Clarify requirements, group_id: design-research }
      - { key: draft_interaction_flow, label: Interaction draft, group_id: design-ux }
  develop:
    operation_primitives:
      - architecture_tradeoff
      - implementation_execution
      - quality_validation
```

---

## 8. Validate and inspect

```bash
python -m saddle mode validate collab_explicit
python -m saddle mode show collab_explicit
```

The merged payload includes normalized `groups` and `primitives` (generated `id`s and filled schemas).

---

## 9. See also

- Mode files, CLI, `--set`, Studio: **[`MODES.md`](./MODES.md)**
- HTTP / plugins and pipeline: **[`PLUGIN_HTTP.md`](./PLUGIN_HTTP.md)**

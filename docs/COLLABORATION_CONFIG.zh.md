# Saddle 智能协作：`collaboration_config` 配置说明

[English version](./COLLABORATION_CONFIG.md)

本文说明 Saddle 模式中**智能协作**相关的配置层次、**操作原语**（分组 `groups`、步骤 `primitives`、简写 `operation_primitives`）及可复制的 YAML 示例。归一化与默认值实现见源码：[`src/saddle/modes/collaboration_payload.py`](../src/saddle/modes/collaboration_payload.py)。

---

## 1. 三层结构（从宏观到微观）

1. **流水线（Pipeline）**  
   默认 **`spec → design → develop`**，由 `pipeline.order` 与各阶段 `enabled` 控制执行顺序与是否跳过某阶段。

2. **阶段编排（design / develop）**  
   各阶段可有 `deep_loop`、`max_iters`、`prompt_profile`（`full` / `compact`）等，控制多轮深循环与提示体量。与模式根下的 `agent_selection`、`thresholds`、`tool_policy`、`role_mindsets` 等共同构成「团队如何跑」。

3. **`collaboration_config`（协作原语）**  
   仅针对 **`design`** 与 **`develop`** 两个阶段，描述：
   - **分组（groups）**：泳道式组织（`id`、`label`、`order`）；
   - **原语（primitives）**：可命名的协作步骤（`key` 必填，可选约束与 JSON Schema）；
   - **`collaboration_format`**：若干字符串键值，与内置默认**浅合并**，用于描述团队/模式/默认产出/交接语义；
   - **`operation_primitives`**：字符串列表简写，由运行时展开为完整 `primitives` 并挂到**默认分组**上。

若 YAML 中**不写** `collaboration_config`，加载模式时会注入代码中的**默认分组 + 默认原语列表**（与 `_default_design_stage` / `_default_develop_stage` 一致）。

---

## 2. `collaboration_config` 顶层形状

```yaml
collaboration_config:
  design:    # 可选；缺省则仅使用默认 design 块
    collaboration_format: { ... }   # 可选；与默认字符串字典合并
    groups: [ ... ]                 # 与 primitives 联用，见下文
    primitives: [ ... ]             # 对象列表，完整原语
    operation_primitives: [ ... ]    # 字符串列表，简写（与 primitives 二选一逻辑见第 4 节）
  develop:
    # 同上
```

**注意**：若同时存在合法的 **`primitives`（非空且首项为对象）** 与 **`operation_primitives`**，归一化以 **`primitives` 分支**为准（`operation_primitives` 被忽略）。

---

## 3. 分组（`groups`）

每项为对象：

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | 是 | 分组唯一标识；`primitives[].group_id` 引用此值 |
| `label` | 否 | 展示用标签；缺省为 `id` |
| `order` | 否 | 数字，用于排序；缺省为当前列表长度 |

内置 **design** 默认 `id`：`design-research`、`design-ux`、`design-review`。  
内置 **develop** 默认 `id`：`dev-planning`、`dev-execution`、`dev-quality`。

---

## 4. 原语（`primitives`）与简写（`operation_primitives`）

### 4.1 完整原语对象

| 字段 | 必填 | 说明 |
|------|------|------|
| `key` | 是 | 步骤语义标识（稳定键） |
| `id` | 否 | 实例 id；省略时由运行时生成 |
| `label` | 否 | 展示用；缺省为 `key` |
| `group_id` | 否 | 对应 `groups[].id`；可为内置默认分组 id |
| `constraints` | 否 | 字符串数组，协作/提示用约束 |
| `input_schema` / `output_schema` | 否 | 须为 **object 类型的 dict**（JSON Schema）；非法或缺失时回落为「空 object + `additionalProperties: true`」 |

### 4.2 仅有 `primitives`、未写 `groups`

当 `primitives` 非空且首元素为 **dict** 时：若未提供有效 `groups`，则**自动使用该阶段的默认 `groups`**（design 三列或 develop 三列）。

### 4.3 `operation_primitives` 下标 → 默认分组

仅当**未**走「完整 `primitives` 对象列表」分支时，非空字符串列表会展开为原语，并按**下标**挂到默认分组：

**Design**（索引 `i` 从 0 开始）：

- `i ≤ 1` → `design-research`
- `2 ≤ i ≤ 4` → `design-ux`
- `i ≥ 5` → `design-review`

**Develop**：

- `i ≤ 2` → `dev-planning`
- `3 ≤ i ≤ 4` → `dev-execution`
- `i ≥ 5` → `dev-quality`

---

## 5. `collaboration_format`

与对应阶段的默认 `collaboration_format` 做**字符串级浅合并**（只覆盖你在 YAML 中写的键）。常见键包括：`team`、`mode`、`default_output`、`handoff`（具体以默认字典为准）。

---

## 6. 与内置模式的关系

仓库内置 **`.saddle/modes/default.yaml`**、**`fast.yaml`**、**`deep.yaml`** 主要调节流水线、`design`/`develop` 轮次与 `agent_selection`、`thresholds` 等；通常**不**内联 `collaboration_config`。需要自定义分组/步骤时，在自定义模式 YAML 中增加 `collaboration_config` 即可。

---

## 7. 配置示例

### 示例 A：只改 `collaboration_format`，原语与分组用默认

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
      team: "产品与设计双轨"
      default_output: "可交给开发的界面与交互说明"
  develop:
    collaboration_format:
      team: "工程交付小队"
      handoff: "合并前自检清单完成"
```

### 示例 B：`operation_primitives`（design：6 步映射到 research / ux / review）

```yaml
collaboration_config:
  design:
    collaboration_format:
      mode: "轻量设计评审"
    operation_primitives:
      - clarify_business_goal
      - list_unknowns
      - user_flow_sketch
      - screen_outline
      - data_contract_draft
      - signoff_for_dev
```

### 示例 C：`operation_primitives`（develop：6 步映射到 planning / execution / quality）

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

### 示例 D：自定义 `groups` + 完整 `primitives`

```yaml
collaboration_config:
  design:
    collaboration_format:
      team: "安全设计小组"
      default_output: "威胁模型与控制措施"
    groups:
      - { id: threat, label: "威胁建模", order: 0 }
      - { id: controls, label: "控制与验收", order: 1 }
    primitives:
      - key: asset_inventory
        label: 资产与信任边界
        group_id: threat
        constraints:
          - 列出数据存储与外部依赖
        input_schema: { type: object, properties: {}, additionalProperties: true }
        output_schema: { type: object, properties: {}, additionalProperties: true }
      - key: control_backlog
        label: 控制项清单
        group_id: controls
        constraints:
          - 每条控制需可验证
        input_schema: { type: object, properties: {}, additionalProperties: true }
        output_schema: { type: object, properties: {}, additionalProperties: true }
```

### 示例 E：完整 `primitives` + 复用内置 develop 分组 id（不写 `groups`）

```yaml
collaboration_config:
  develop:
    collaboration_format:
      default_output: "带测试的增量 PR 说明"
    primitives:
      - key: scope_decomposition
        label: 范围拆解
        group_id: dev-planning
        constraints: ["每个切片可独立合并"]
      - key: implementation_execution
        label: 实现与自测
        group_id: dev-execution
      - key: quality_validation
        label: 质量门禁
        group_id: dev-quality
        constraints: ["明确退出标准"]
```

### 示例 F：两阶段同时声明

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
      - { id: design-research, label: "对齐", order: 0 }
      - { id: design-ux, label: "方案", order: 1 }
    primitives:
      - { key: clarify_requirement, label: 澄清需求, group_id: design-research }
      - { key: draft_interaction_flow, label: 交互草案, group_id: design-ux }
  develop:
    operation_primitives:
      - architecture_tradeoff
      - implementation_execution
      - quality_validation
```

---

## 8. 校验与查看

```bash
python -m saddle mode validate collab_explicit
python -m saddle mode show collab_explicit
```

合并输出中的 `collaboration_config` 会包含归一化后的 `groups`、`primitives`（含生成的 `id` 与补全的 schema）。

---

## 9. 相关文档

- 模式文件路径、CLI、`--set`、Studio：**[`MODES.md`](./MODES.md)**
- HTTP / 插件触发流水线：**[`PLUGIN_HTTP.md`](./PLUGIN_HTTP.md)**

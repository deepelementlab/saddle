# Saddle 插件 HTTP 契约

本文档描述 **`saddle serve`**（默认 `http://127.0.0.1:1995`）对外暴露的、供 **Claude Code 插件**与 **OpenClaw context-engine 插件**使用的 REST 形状。实现以 [memory_api/server.py](../src/saddle/memory_api/server.py) 为准。

## 环境变量（客户端）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SADDLE_BASE_URL` | API 根 URL，无尾部 `/` | `http://127.0.0.1:1995` |
| `SADDLE_GROUP_ID` | 记忆分组 ID（多项目隔离） | `saddle-default-group` |
| `SADDLE_USER_ID` | 用户/主体 ID | `saddle-user` |

Claude Code 插件与 OpenClaw 插件在各自 `README` 中可能使用插件配置覆盖上述值。

## 服务端环境

| 变量 | 说明 |
|------|------|
| `SADDLE_MEMORY_DIR` | 记忆 JSONL 存储目录，默认 `<cwd>/.saddle/memory` |

**安全说明**：当前 API **无鉴权**，仅建议本机或受信网络使用。若将 `saddle serve` 绑定 `0.0.0.0` 暴露到公网，需自行加反向代理与认证。

---

## `GET /health`

**响应示例**

```json
{ "status": "healthy", "service": "saddle-memory" }
```

---

## `POST /api/v1/memories`

与 `POST /api/v1/memories/group` 等价（别名）。

**请求体**（`GroupPayload`）

| 字段 | 类型 | 说明 |
|------|------|------|
| `group_id` | string | 分组 ID |
| `user_id` | string | 用户 ID |
| `messages` | array | 每条：`{ "role": "user"\|"assistant", "content": string, "timestamp"?: number }`（毫秒，可选） |
| `async_mode` | bool | 保留字段，默认 `true` |

**响应**：包含 `status`、`count`、`request_id` 等（见实现）。

---

## `POST /api/v1/memories/search`

**请求体**（`SearchPayload`）

| 字段 | 类型 | 说明 |
|------|------|------|
| `query` | string | 检索词 |
| `top_k` | int | 返回条数上限 |
| `filters` | object 或 null | 可含 `group_id` 字符串，限定分组 |

**响应**

```json
{
  "data": {
    "memories": [
      {
        "id": "...",
        "group_id": "...",
        "user_id": "...",
        "role": "user",
        "content": "...",
        "timestamp": 1710000000000,
        "memory_type": "episodic_memory",
        "score": 0.85
      }
    ],
    "count": 1
  }
}
```

检索实现为本地 JSONL 上的简单关键词匹配，**非向量检索**；与云端记忆产品的质量不可直接类比。

---

## `POST /api/v1/memories/get`

**请求体**（`GetPayload`）

| 字段 | 类型 | 说明 |
|------|------|------|
| `filters` | object 或 null | 可含 `group_id` |
| `page` | int | 页码，从 1 起 |
| `page_size` | int | 每页条数 |

**响应**：`data` 内含 `episodes`、`total_count` 等（见 [MemoryStore.get](../src/saddle/memory_api/store.py)）。

---

## `GET /api/v1/modes`

列出当前工作目录下 `.saddle/modes` 中的模式名（`cwd` 为 `saddle serve` 进程工作目录）。

**响应示例**

```json
{
  "modes": ["default", "fast", "deep"],
  "path": "/path/to/project/.saddle/modes"
}
```

## `GET /api/v1/modes/{name}`

返回合并解析后的模式配置（含 `pipeline`、`spec`/`design`/`develop` 等）。404 时返回错误详情。

---

## `POST /api/v1/pipeline/run`

与 CLI **`saddle run`** 等价：在指定 **`project_root`** 上执行 [`PipelineRunner`](../src/saddle/pipeline/runner.py)（`resolve_mode` + 各 stage）。

**请求体**

| 字段 | 类型 | 说明 |
|------|------|------|
| `requirement` | string | 需求描述（必填） |
| `mode` | string | 模式名，默认 `default` |
| `set` | string 数组，可选 | 与 CLI `--set` 相同，如 `develop.max_iters=20` |
| `project_root` | string，可选 | 项目根绝对路径；省略则使用 **`saddle serve` 进程当前工作目录** |
| `session_id` | string，可选 | 会话 ID；省略则服务端生成 UUID |

**响应示例**

```json
{
  "ok": true,
  "project_root": "/path/to/project",
  "result": {
    "mode": "fast",
    "session_id": "...",
    "stages": []
  }
}
```

**安全**：与全文一致，**无鉴权**；勿将 `saddle serve` 暴露公网。`project_root` 仅做存在性与目录校验；勿指向无关敏感路径。流水线可能 **长时间阻塞**，与 CLI 行为一致。

---

## 与 EverOS 后端的差异

EverOS 示例插件常使用 **GET** `/api/v1/memories/search`（query 参数）及不同形状的 **POST** 单条写入。Saddle 插件 **必须**使用本文档中的 **POST JSON** 契约；不要在未加兼容层的情况下混接 EverOS 客户端与 Saddle 服务端。

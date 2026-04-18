import { request } from "./http.js";

const noop = { info() {}, warn() {} };
const TAG = "[saddle-ai-openclaw]";

/**
 * Search memories via Saddle POST /api/v1/memories/search.
 * @param {import("./types.js").SaddleConfig} cfg
 * @param {Record<string, unknown>} params - query, top_k, user_id, group_id, memory_types, retrieve_method
 */
export async function searchMemories(cfg, params, log = noop) {
  const groupId = params.group_id ?? cfg.groupId;
  const query = String(params.query ?? "");
  const topK = params.top_k ?? cfg.topK ?? 5;

  const body = {
    query,
    top_k: topK,
    filters: groupId ? { group_id: groupId } : null,
  };

  log.info(`${TAG} POST /api/v1/memories/search`);
  const r = await request(cfg, "POST", "/api/v1/memories/search", body);

  let memories = r?.data?.memories ?? [];
  const wantTypes = new Set(params.memory_types ?? cfg.memoryTypes ?? ["episodic_memory"]);
  if (wantTypes.size) {
    memories = memories.filter((m) => wantTypes.has(m.memory_type));
  }

  return {
    status: "ok",
    result: {
      memories,
      pending_messages: [],
    },
  };
}

/**
 * Save messages via Saddle POST /api/v1/memories (batch GroupPayload).
 */
export async function saveMemories(cfg, { userId, groupId, messages = [] }) {
  if (!messages.length) return;

  const stamp = Date.now();
  const payloads = messages.map((msg, i) => {
    const { role = "user", content = "" } = msg;
    return {
      role,
      content,
      timestamp: stamp + i,
    };
  });

  await request(cfg, "POST", "/api/v1/memories", {
    group_id: groupId,
    user_id: userId,
    messages: payloads,
    async_mode: true,
  });
}

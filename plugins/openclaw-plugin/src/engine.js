function toText(content) {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) return content.map((x) => (typeof x === "string" ? x : x?.text || "")).join("\n");
  return "";
}

async function search(cfg, query) {
  const resp = await fetch(`${cfg.baseUrl}/api/v1/memories/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: cfg.topK, filters: { group_id: cfg.groupId } }),
  });
  if (!resp.ok) return [];
  const data = await resp.json();
  return data?.data?.memories || [];
}

async function save(cfg, messages) {
  await fetch(`${cfg.baseUrl}/api/v1/memories/group`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      group_id: cfg.groupId,
      user_id: cfg.userId,
      messages,
      async_mode: true,
    }),
  });
}

export function createContextEngine(meta, pluginConfig, logger) {
  const cfg = {
    baseUrl: pluginConfig?.baseUrl || "http://127.0.0.1:1995",
    userId: pluginConfig?.userId || "saddle-user",
    groupId: pluginConfig?.groupId || "openclaw-default",
    topK: Number(pluginConfig?.topK || 5),
  };
  const state = new Map();
  return {
    info: { id: meta.id, name: meta.name, version: meta.version, ownsCompaction: false },
    async bootstrap({ sessionKey }) {
      state.set(sessionKey, { savedUpTo: 0, turn: 0 });
      return { bootstrapped: true };
    },
    async ingest() {
      return { ingested: true };
    },
    async ingestBatch({ messages }) {
      return { ingestedCount: messages?.length || 0 };
    },
    async assemble({ sessionKey, messages, prompt }) {
      const query = toText(prompt) || toText([...messages].reverse().find((m) => m?.role === "user")?.content);
      if (!query || query.length < 3) return { messages, estimatedTokens: 0 };
      const hits = await search(cfg, query);
      if (!hits.length) return { messages, estimatedTokens: 0 };
      const context = hits
        .slice(0, cfg.topK)
        .map((h, i) => `[${i + 1}] ${(h.content || "").slice(0, 200)}`)
        .join("\n");
      logger.info?.(`[${meta.id}] assemble memories=${hits.length}`);
      return { messages, estimatedTokens: Math.floor(context.length / 4), systemPromptAddition: `<memory>\n${context}\n</memory>` };
    },
    async afterTurn({ sessionKey, messages }) {
      const s = state.get(sessionKey) || { savedUpTo: 0, turn: 0 };
      s.turn += 1;
      const delta = messages.slice(s.savedUpTo).filter((m) => m?.role === "user" || m?.role === "assistant");
      if (delta.length) {
        await save(
          cfg,
          delta.map((m) => ({ role: m.role, content: toText(m.content), timestamp: Date.now() }))
        );
        s.savedUpTo = messages.length;
      }
      state.set(sessionKey, s);
    },
    async compact() {
      return { ok: true, compacted: false, reason: "host_compaction_preferred" };
    },
    async dispose({ sessionKey } = {}) {
      if (sessionKey) state.delete(sessionKey);
      else state.clear();
    },
  };
}

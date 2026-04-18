import { getBaseUrl, getGroupId, getUserId } from "./config.js";

/**
 * POST /api/v1/memories/search
 */
export async function searchMemories(query, { topK = 15 } = {}) {
  const base = getBaseUrl();
  const res = await fetch(`${base}/api/v1/memories/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      top_k: topK,
      filters: { group_id: getGroupId() },
    }),
    signal: AbortSignal.timeout(20000),
  });
  if (!res.ok) {
    const t = await res.text().catch(() => "");
    throw new Error(`search ${res.status} ${t.slice(0, 200)}`);
  }
  return res.json();
}

/**
 * Map API JSON to inject-memories display rows.
 */
export function transformSearchResults(apiResponse) {
  const memories = apiResponse?.data?.memories ?? [];
  return memories.map((m) => ({
    score: typeof m.score === "number" ? m.score : 0.5,
    subject: "",
    text: String(m.content || ""),
    timestamp: m.timestamp != null ? new Date(Number(m.timestamp)) : new Date(),
  }));
}

/**
 * Batch append messages (one HTTP call).
 */
export async function appendMessages(messages) {
  const base = getBaseUrl();
  const res = await fetch(`${base}/api/v1/memories`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      group_id: getGroupId(),
      user_id: getUserId(),
      messages,
      async_mode: true,
    }),
    signal: AbortSignal.timeout(30000),
  });
  if (!res.ok) {
    const t = await res.text().catch(() => "");
    throw new Error(`append ${res.status} ${t.slice(0, 200)}`);
  }
  return res.json();
}

export async function getHealth() {
  const base = getBaseUrl();
  const res = await fetch(`${base}/health`, { signal: AbortSignal.timeout(5000) });
  return res.ok;
}

export async function getRecentMemories(pageSize = 5) {
  const base = getBaseUrl();
  const res = await fetch(`${base}/api/v1/memories/get`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      filters: { group_id: getGroupId() },
      page: 1,
      page_size: pageSize,
    }),
    signal: AbortSignal.timeout(15000),
  });
  if (!res.ok) return null;
  return res.json();
}

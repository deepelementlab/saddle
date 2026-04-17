const baseUrl = process.env.SADDLE_BASE_URL || process.env.EVERMEM_BASE_URL || "http://127.0.0.1:1995";
const userId = process.env.SADDLE_USER_ID || "saddle-user";

export async function readHookInput() {
  let input = "";
  for await (const chunk of process.stdin) input += chunk;
  try {
    return JSON.parse(input || "{}");
  } catch {
    return {};
  }
}

export function groupIdFromCwd(cwd) {
  return `claude-code:${cwd || "unknown"}`;
}

export async function searchMemories(query, groupId) {
  const resp = await fetch(`${baseUrl}/api/v1/memories/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: 5, filters: { group_id: groupId } }),
  });
  if (!resp.ok) return [];
  const data = await resp.json();
  return (data?.data?.memories || []);
}

export async function saveMessages(groupId, messages) {
  const resp = await fetch(`${baseUrl}/api/v1/memories/group`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ group_id: groupId, user_id: userId, messages, async_mode: true }),
  });
  if (!resp.ok) return false;
  return true;
}

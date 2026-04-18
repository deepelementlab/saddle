/**
 * Strip channel-injected metadata blocks from message text.
 */
export function stripChannelMetadata(text) {
  if (!text) return text;
  let cleaned = text.replace(/(?:Conversation info|Sender)\s*\(untrusted metadata\)\s*:\s*```json[\s\S]*?```/gi, "");
  cleaned = cleaned.replace(/\[message_id:\s*[^\]]*\]\s*\n?\s*\S+:\s*/g, "");
  cleaned = cleaned.trim();
  cleaned = cleaned.replace(/^\[(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+GMT[+-]\d+\]\s*/i, "");
  return cleaned.trim();
}

export function toText(content) {
  if (!content) return "";
  if (typeof content === "string") return stripChannelMetadata(content);
  if (!Array.isArray(content)) return "";
  const raw = content.reduce((out, block) => {
    if (block?.type !== "text" || !block.text) return out;
    return out ? `${out} ${block.text}` : block.text;
  }, "");
  return stripChannelMetadata(raw);
}

export const BARE_SESSION_RESET_PROMPT =
  "A new session was started via /new or /reset. Execute your Session Startup sequence now - read the required files before responding to the user. Then greet the user in your configured persona, if one is provided. Be yourself - use your defined voice, mannerisms, and mood. Keep it to 1-3 sentences and ask what they want to do. If the runtime model differs from default_model in the system prompt, mention the default model. Do not mention internal steps, files, tools, or reasoning.";

function levenshtein(a, b) {
  const m = a.length;
  const n = b.length;
  const prev = Array.from({ length: n + 1 }, (_, i) => i);
  const curr = new Array(n + 1);
  for (let i = 1; i <= m; i++) {
    curr[0] = i;
    for (let j = 1; j <= n; j++) {
      curr[j] =
        a[i - 1] === b[j - 1] ? prev[j - 1] : 1 + Math.min(prev[j - 1], prev[j], curr[j - 1]);
    }
    prev.splice(0, n + 1, ...curr);
  }
  return prev[n];
}

export function isSessionResetPrompt(query) {
  if (!query) return false;
  const promptLen = BARE_SESSION_RESET_PROMPT.length;
  const queryLen = query.length;
  if (Math.abs(queryLen - promptLen) / promptLen > 0.20) return false;
  const dist = levenshtein(query, BARE_SESSION_RESET_PROMPT);
  return dist / Math.max(queryLen, promptLen) < 0.20;
}

import { CONTEXT_BOUNDARY } from "./prompt.js";
import { stripChannelMetadata } from "./messages.js";

const MAX_CHARS = 20000;

function stripContext(text) {
  if (!text) return text;
  const cut = text.lastIndexOf(CONTEXT_BOUNDARY);
  return cut < 0 ? text : text.slice(cut + CONTEXT_BOUNDARY.length).replace(/^\s+/, "");
}

function cap(s) {
  return s && s.length > MAX_CHARS ? `${s.slice(0, MAX_CHARS)}…` : (s || "");
}

/**
 * Convert OpenClaw AgentMessage to Saddle message format.
 * @param {Object} msg - OpenClaw AgentMessage
 * @returns {{ role: string, content: string }}
 */
export function convertMessage(msg) {
  const content = msg.content;
  let role = msg.role;
  let textContent = "";

  if (role !== "user" && role !== "assistant") {
    return { role: "user", content: "" };
  }

  if (typeof content === "string") {
    const clean = role === "user" ? cap(stripChannelMetadata(stripContext(content))) : cap(content);
    return { role, content: clean };
  }

  if (Array.isArray(content)) {
    for (const block of content) {
      if (!block || !block.type) continue;

      if (block.type === "text") {
        const text = block.text ?? "";
        textContent += (textContent ? "\n" : "") + text;
      } else if (block.type === "toolCall" || block.type === "tool_use") {
        textContent += (textContent ? "\n" : "") + `[Tool: ${block.name || "unknown"}]`;
      } else if (block.type === "tool_result") {
        continue;
      }
    }

    if (role === "assistant" && /^\s*(\[Tool:\s*[^\]]*\]\s*)+$/.test(textContent)) {
      return { role, content: "" };
    }

    const finalText = role === "user" ? cap(stripChannelMetadata(stripContext(textContent))) : cap(textContent);
    return { role, content: finalText || "" };
  }

  return { role, content: cap(content == null ? "" : String(content)) };
}

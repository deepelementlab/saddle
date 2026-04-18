#!/usr/bin/env node

process.on("uncaughtException", () => process.exit(0));
process.on("unhandledRejection", () => process.exit(0));

import { readFileSync, existsSync } from "node:fs";
import { appendMessages } from "./utils/saddle-api.js";
import { isDisabled } from "./utils/config.js";
import { debug } from "./utils/debug.js";

async function readTranscriptWithRetry(path, maxRetries = 5, delayMs = 100) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    const content = readFileSync(path, "utf8");
    const lines = content.trim().split("\n");

    let isComplete = false;
    try {
      const lastLine = JSON.parse(lines[lines.length - 1]);
      isComplete = lastLine.type === "system" && lastLine.subtype === "turn_duration";
    } catch {
      /* ignore */
    }

    if (isComplete) {
      return lines;
    }

    if (attempt < maxRetries) {
      await new Promise((r) => setTimeout(r, delayMs));
    }
  }

  const content = readFileSync(path, "utf8");
  return content.trim().split("\n");
}

function hasContent(text) {
  return text && text.trim().length > 0;
}

function extractLastTurn(lines) {
  const turnEndIndex = lines.length;
  let turnStartIndex = 0;
  for (let i = lines.length - 1; i >= 0; i--) {
    try {
      const e = JSON.parse(lines[i]);
      if (e.type === "system" && e.subtype === "turn_duration") {
        turnStartIndex = i + 1;
        break;
      }
    } catch {
      /* ignore */
    }
  }

  const userTexts = [];
  const assistantTexts = [];

  for (let i = turnStartIndex; i < turnEndIndex; i++) {
    try {
      const e = JSON.parse(lines[i]);
      const content = e.message?.content;

      if (e.type === "user") {
        if (typeof content === "string") {
          userTexts.push(content);
        } else if (Array.isArray(content)) {
          for (const block of content) {
            if (block.type === "text" && block.text) {
              userTexts.push(block.text);
            }
          }
        }
      }

      if (e.type === "assistant") {
        if (Array.isArray(content)) {
          for (const block of content) {
            if (block.type === "text" && block.text) {
              assistantTexts.push(block.text);
            }
          }
        } else if (typeof content === "string") {
          assistantTexts.push(content);
        }
      }
    } catch {
      /* ignore */
    }
  }

  return {
    user: userTexts.join("\n\n"),
    assistant: assistantTexts.join("\n\n"),
  };
}

try {
  if (isDisabled()) {
    process.exit(0);
  }

  let input = "";
  for await (const chunk of process.stdin) {
    input += chunk;
  }

  const hookInput = JSON.parse(input);
  const transcriptPath = hookInput.transcript_path;

  if (hookInput.cwd) {
    process.env.SADDLE_CWD = hookInput.cwd;
  }

  if (!transcriptPath || !existsSync(transcriptPath)) {
    process.exit(0);
  }

  const lines = await readTranscriptWithRetry(transcriptPath);
  const lastTurn = extractLastTurn(lines);
  const lastUser = lastTurn.user;
  const lastAssistant = lastTurn.assistant;

  const messages = [];
  const now = Date.now();
  if (hasContent(lastUser)) {
    messages.push({ role: "user", content: lastUser.trim(), timestamp: now });
  }
  if (hasContent(lastAssistant)) {
    messages.push({ role: "assistant", content: lastAssistant.trim(), timestamp: now + 1 });
  }

  if (messages.length === 0) {
    process.exit(0);
  }

  try {
    await appendMessages(messages);
    const detail = messages.map((m) => `${m.role}:${m.content.length}`).join(", ");
    process.stdout.write(
      JSON.stringify({
        systemMessage: `Saddle: saved ${messages.length} message(s) [${detail}]`,
      }),
    );
  } catch (e) {
    debug("append error:", e.message);
    process.stdout.write(
      JSON.stringify({
        systemMessage: `Saddle: save failed — ${e.message}. Is saddle serve running?`,
      }),
    );
  }
} catch {
  process.exit(0);
}

#!/usr/bin/env node

import { searchMemories, transformSearchResults } from "./utils/saddle-api.js";
import { isDisabled } from "./utils/config.js";
import { debug } from "./utils/debug.js";

const MIN_WORDS = 3;
const MAX_MEMORIES = 5;
const MIN_SCORE = 0.1;

function countWords(text) {
  if (!text) return 0;
  const trimmed = text.trim();
  if (!trimmed) return 0;
  const cjkRegex = /[\u4E00-\u9FFF\u3400-\u4DBF\u3040-\u309F\u30A0-\u30FF\uAC00-\uD7AF]/g;
  const cjkMatches = trimmed.match(cjkRegex);
  const cjkCount = cjkMatches ? cjkMatches.length : 0;
  const nonCjkText = trimmed.replace(cjkRegex, " ").trim();
  const wordCount = nonCjkText ? nonCjkText.split(/\s+/).filter((w) => w.length > 0).length : 0;
  return cjkCount + wordCount;
}

function formatRelativeTime(date) {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) return "unknown";
  const diffMs = Date.now() - date.getTime();
  const minutes = Math.floor(diffMs / 60000);
  const hours = Math.floor(diffMs / 3600000);
  const days = Math.floor(diffMs / 86400000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 30) return `${days}d ago`;
  return `${Math.floor(days / 30)}mo ago`;
}

function readStdin() {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => {
      data += chunk;
    });
    process.stdin.on("end", () => resolve(data));
    process.stdin.on("error", reject);
  });
}

function buildDisplayMessage(memories) {
  const header = `Saddle memory (${memories.length}):`;
  const lines = [header];
  for (const memory of memories) {
    const relTime = formatRelativeTime(memory.timestamp);
    const score = memory.score ? memory.score.toFixed(2) : "0.00";
    const title =
      memory.subject ||
      (memory.text.length > 60 ? `${memory.text.slice(0, 60)}...` : memory.text);
    lines.push(`  • [${score}] (${relTime}) ${title}`);
  }
  return lines.join("\n");
}

function buildContext(memories) {
  const sortedMemories = [...memories].sort((a, b) => {
    const timeA = a.timestamp ? a.timestamp.getTime() : 0;
    const timeB = b.timestamp ? b.timestamp.getTime() : 0;
    return timeB - timeA;
  });

  const lines = [
    "<relevant-memories>",
    "Context from past sessions (Saddle local store):",
    "",
  ];

  for (const memory of sortedMemories) {
    const timeStr = memory.timestamp
      ? memory.timestamp.toISOString().replace("T", " ").slice(0, 19) + " UTC"
      : "Unknown time";
    lines.push(`[${timeStr}]`);
    lines.push(memory.text);
    lines.push("");
  }

  lines.push("</relevant-memories>");
  return lines.join("\n");
}

async function main() {
  try {
    if (isDisabled()) {
      process.exit(0);
    }

    const input = await readStdin();
    const data = JSON.parse(input);
    const prompt = data.prompt || "";

    if (data.cwd) {
      process.env.SADDLE_CWD = data.cwd;
    }

    const wordCount = countWords(prompt);
    if (wordCount < MIN_WORDS) {
      process.exit(0);
    }

    let memories = [];
    try {
      const apiResponse = await searchMemories(prompt, { topK: 15 });
      memories = transformSearchResults(apiResponse);
    } catch (error) {
      debug("search error:", error.message);
      process.exit(0);
    }

    const relevantMemories = memories.filter((m) => m.score >= MIN_SCORE);
    if (relevantMemories.length === 0) {
      process.exit(0);
    }

    const selectedMemories = relevantMemories.slice(0, MAX_MEMORIES);
    const context = buildContext(selectedMemories);
    const displayMessage = buildDisplayMessage(selectedMemories);

    const output = {
      systemMessage: displayMessage,
      hookSpecificOutput: {
        hookEventName: "UserPromptSubmit",
        additionalContext: context,
      },
    };

    process.stdout.write(JSON.stringify(output));
    process.exit(0);
  } catch {
    process.exit(0);
  }
}

main();

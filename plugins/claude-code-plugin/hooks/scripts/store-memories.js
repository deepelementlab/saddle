#!/usr/bin/env node
import fs from "node:fs";
import { groupIdFromCwd, readHookInput, saveMessages } from "./utils.js";

function readLastTurnText(path) {
  if (!path || !fs.existsSync(path)) return { user: "", assistant: "" };
  const lines = fs.readFileSync(path, "utf8").split("\n").filter(Boolean);
  let user = "";
  let assistant = "";
  for (const line of lines.slice(-100).reverse()) {
    try {
      const row = JSON.parse(line);
      if (!assistant && row?.type === "assistant") {
        const c = row?.message?.content;
        if (typeof c === "string") assistant = c;
        if (Array.isArray(c)) {
          const t = c.filter((x) => x?.type === "text").map((x) => x?.text || "").join("\n");
          if (t) assistant = t;
        }
      } else if (!user && row?.type === "user") {
        const c = row?.message?.content;
        if (typeof c === "string") user = c;
      }
      if (user && assistant) break;
    } catch {}
  }
  return { user, assistant };
}

const input = await readHookInput();
const groupId = groupIdFromCwd(input.cwd);
const { user, assistant } = readLastTurnText(input.transcript_path);
const now = Date.now();
const messages = [];
if (user) messages.push({ role: "user", content: user, timestamp: now });
if (assistant) messages.push({ role: "assistant", content: assistant, timestamp: now + 1 });

if (!messages.length) {
  console.log(JSON.stringify({ continue: true, systemMessage: "Saddle: no message extracted." }));
  process.exit(0);
}

const ok = await saveMessages(groupId, messages);
console.log(JSON.stringify({ continue: true, systemMessage: ok ? "Saddle: memory saved." : "Saddle: save failed." }));

#!/usr/bin/env node
import { groupIdFromCwd, readHookInput, searchMemories } from "./utils.js";

const input = await readHookInput();
const groupId = groupIdFromCwd(input.cwd);
const memories = await searchMemories("session", groupId);
const preview = memories.slice(0, 3).map((m) => `- ${String(m.content || "").slice(0, 120)}`).join("\n");

console.log(
  JSON.stringify({
    continue: true,
    systemMessage: memories.length ? `Saddle: loaded ${memories.length} recent memories.` : "Saddle: no session memory.",
    systemPrompt: preview ? `<session-context>\n${preview}\n</session-context>` : undefined,
  })
);

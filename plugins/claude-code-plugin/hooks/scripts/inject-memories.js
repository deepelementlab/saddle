#!/usr/bin/env node
import { groupIdFromCwd, readHookInput, searchMemories } from "./utils.js";

const input = await readHookInput();
const prompt = input.prompt || "";
const groupId = groupIdFromCwd(input.cwd);

if (!prompt || prompt.trim().length < 3) {
  console.log(JSON.stringify({ continue: true }));
  process.exit(0);
}

const memories = await searchMemories(prompt, groupId);
if (!memories.length) {
  console.log(JSON.stringify({ continue: true, systemMessage: "Saddle: no related memories found." }));
  process.exit(0);
}

const lines = memories
  .slice(0, 5)
  .map((m, i) => `[${i + 1}] (${m.score ?? 0}) ${String(m.content || "").slice(0, 240)}`);
const systemPrompt = `<saddle-memory>\n${lines.join("\n")}\n</saddle-memory>`;
console.log(
  JSON.stringify({
    continue: true,
    systemMessage: `Saddle: retrieved ${memories.length} memories.`,
    systemPrompt,
  })
);

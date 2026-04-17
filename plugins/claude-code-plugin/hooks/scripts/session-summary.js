#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { readHookInput } from "./utils.js";

const input = await readHookInput();
const dataDir = path.join(process.cwd(), ".saddle", "plugin-data");
fs.mkdirSync(dataDir, { recursive: true });
const file = path.join(dataDir, "sessions.jsonl");
const row = {
  sessionId: input.session_id || "",
  cwd: input.cwd || "",
  reason: input.reason || "unknown",
  timestamp: new Date().toISOString(),
};
fs.appendFileSync(file, `${JSON.stringify(row)}\n`);
console.log(JSON.stringify({ continue: true, systemMessage: "Saddle: session summary saved." }));

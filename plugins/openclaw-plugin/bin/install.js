#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const home = os.homedir();
const cfgDir = path.join(home, ".openclaw");
const cfgPath = path.join(cfgDir, "openclaw.json");
fs.mkdirSync(cfgDir, { recursive: true });

let cfg = {};
if (fs.existsSync(cfgPath)) {
  try {
    cfg = JSON.parse(fs.readFileSync(cfgPath, "utf8"));
  } catch {
    cfg = {};
  }
}

cfg.plugins = cfg.plugins || {};
cfg.plugins.allow = Array.from(new Set([...(cfg.plugins.allow || []), "saddle-openclaw-memory"]));
cfg.plugins.slots = cfg.plugins.slots || {};
cfg.plugins.slots.memory = "none";
cfg.plugins.slots.contextEngine = "saddle-openclaw-memory";
cfg.plugins.entries = cfg.plugins.entries || {};
cfg.plugins.entries["saddle-openclaw-memory"] = {
  enabled: true,
  config: {
    baseUrl: process.env.SADDLE_BASE_URL || "http://127.0.0.1:1995",
    userId: process.env.SADDLE_USER_ID || "saddle-user",
    groupId: process.env.SADDLE_GROUP_ID || "openclaw-default",
    topK: 5,
  },
};

fs.writeFileSync(cfgPath, JSON.stringify(cfg, null, 2));
console.log(`updated ${cfgPath}`);
console.log("please run: openclaw gateway restart");

/**
 * Saddle Claude Code plugin — env and project-scoped group id.
 */

import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const envPath = resolve(__dirname, "../../../.env");

if (existsSync(envPath)) {
  const envContent = readFileSync(envPath, "utf8");
  for (const line of envContent.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const [key, ...valueParts] = trimmed.split("=");
    if (key && valueParts.length > 0) {
      const value = valueParts.join("=").replace(/^["']|["']$/g, "");
      if (!process.env[key]) {
        process.env[key] = value;
      }
    }
  }
}

export function getBaseUrl() {
  return (process.env.SADDLE_BASE_URL || "http://127.0.0.1:1995").replace(/\/*$/, "");
}

export function getUserId() {
  return process.env.SADDLE_USER_ID || "saddle-user";
}

export function getGroupId() {
  if (process.env.SADDLE_GROUP_ID) {
    return process.env.SADDLE_GROUP_ID;
  }
  const cwd = process.env.SADDLE_CWD || process.cwd();
  return `claude-code:${cwd.replace(/\\/g, "/")}`;
}

export function isDisabled() {
  return process.env.SADDLE_DISABLE === "1" || process.env.SADDLE_DISABLE === "true";
}

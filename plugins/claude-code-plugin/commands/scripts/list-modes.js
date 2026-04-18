#!/usr/bin/env node
import { readFileSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, "../../..");
const envPath = resolve(root, ".env");
if (existsSync(envPath)) {
  for (const line of readFileSync(envPath, "utf8").split("\n")) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const i = t.indexOf("=");
    if (i > 0) {
      const k = t.slice(0, i);
      const v = t.slice(i + 1).replace(/^["']|["']$/g, "");
      if (!process.env[k]) process.env[k] = v;
    }
  }
}

const base = (process.env.SADDLE_BASE_URL || "http://127.0.0.1:1995").replace(/\/*$/, "");

const res = await fetch(`${base}/api/v1/modes`);
if (!res.ok) {
  console.error(`HTTP ${res.status}`);
  process.exit(1);
}
const data = await res.json();
console.log(JSON.stringify(data, null, 2));

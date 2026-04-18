#!/usr/bin/env node
/**
 * One-shot: POST /api/v1/pipeline/run (same as `saddle run`).
 * Usage: node run-once.js <requirement> [mode]
 * Env: SADDLE_BASE_URL (default http://127.0.0.1:1995), SADDLE_PROJECT_ROOT (default cwd)
 */

const base = (process.env.SADDLE_BASE_URL || "http://127.0.0.1:1995").replace(/\/*$/, "");
const root = process.env.SADDLE_PROJECT_ROOT || process.cwd();

const argv = process.argv.slice(2);
if (argv.length < 1) {
  console.error("Usage: run-once.js <requirement> [mode]");
  process.exit(1);
}

let requirement;
let mode = "default";
if (argv.length >= 2) {
  mode = argv[argv.length - 1];
  requirement = argv.slice(0, -1).join(" ").trim();
} else {
  requirement = argv[0].trim();
}

const payload = JSON.stringify({
  requirement,
  mode,
  project_root: root,
});

fetch(`${base}/api/v1/pipeline/run`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: payload,
  signal: AbortSignal.timeout(3_600_000),
})
  .then(async (res) => {
    const t = await res.text();
    if (!res.ok) {
      console.error(`HTTP ${res.status}: ${t.slice(0, 2000)}`);
      process.exit(1);
    }
    console.log(t);
  })
  .catch((e) => {
    console.error(e.message);
    process.exit(1);
  });

#!/usr/bin/env node
/**
 * Trigger `saddle run` via POST /api/v1/pipeline/run (preferred), or CLI fallback.
 * Usage: node run-pipeline.js "<requirement>" [--mode MODE]
 *    or: node run-pipeline.js <arg1> <arg2>  → requirement=arg1, mode=arg2 (single-token mode)
 */

import { spawnSync } from "node:child_process";
import { readFileSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const pluginRoot = resolve(__dirname, "../../..");
const envPath = resolve(pluginRoot, ".env");
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

function projectRoot() {
  return (
    process.env.CLAUDE_PROJECT_DIR ||
    process.env.SADDLE_CWD ||
    process.cwd()
  );
}

function parseArgs(argv) {
  if (argv.length >= 2 && !argv.join(" ").includes("--mode")) {
    const mode = argv[argv.length - 1];
    const requirement = argv.slice(0, -1).join(" ").trim();
    if (requirement && /^[\w.-]+$/.test(mode) && mode.length < 64) {
      return { requirement, mode };
    }
  }
  const joined = argv.join(" ").trim();
  if (!joined) {
    return { requirement: "", mode: "default" };
  }
  const m = joined.match(/--mode\s+(\S+)\s*$/);
  if (m) {
    return {
      requirement: joined.replace(/\s*--mode\s+\S+\s*$/, "").trim(),
      mode: m[1],
    };
  }
  return { requirement: joined, mode: "default" };
}

function runCli(requirement, mode, cwd) {
  const py = process.env.SADDLE_PYTHON || "python";
  const r = spawnSync(py, ["-m", "saddle", "run", requirement, "--mode", mode], {
    cwd,
    encoding: "utf8",
    maxBuffer: 50 * 1024 * 1024,
  });
  if (r.error) {
    console.error(String(r.error));
    process.exit(1);
  }
  if (r.stdout) process.stdout.write(r.stdout);
  if (r.stderr) process.stderr.write(r.stderr);
  process.exit(r.status ?? 1);
}

async function main() {
  const argv = process.argv.slice(2);
  const { requirement, mode } = parseArgs(argv);
  if (!requirement) {
    console.error("Usage: requirement text required (and optional --mode NAME).");
    process.exit(1);
  }

  const cwd = projectRoot();
  const body = {
    requirement,
    mode,
    project_root: cwd,
  };

  try {
    const res = await fetch(`${base}/api/v1/pipeline/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(3_600_000),
    });
    const text = await res.text();
    if (!res.ok) {
      console.error(`HTTP ${res.status}: ${text.slice(0, 2000)}`);
      console.error("Falling back to: python -m saddle run ...");
      runCli(requirement, mode, cwd);
      return;
    }
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      process.stdout.write(text);
      process.exit(0);
      return;
    }
    const out = JSON.stringify(data, null, 2);
    const max = 120_000;
    process.stdout.write(out.length > max ? `${out.slice(0, max)}\n… [truncated]\n` : out);
    process.stdout.write("\n");
    process.exit(0);
  } catch (e) {
    console.error(`API error: ${e.message}`);
    console.error("Falling back to: python -m saddle run ...");
    runCli(requirement, mode, cwd);
  }
}

main();

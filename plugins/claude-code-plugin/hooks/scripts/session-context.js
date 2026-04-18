#!/usr/bin/env node

/**
 * SessionStart — show memory count for this project (optional).
 */

import { getRecentMemories, getHealth } from "./utils/saddle-api.js";
import { isDisabled } from "./utils/config.js";

async function main() {
  if (isDisabled()) {
    process.stdout.write(JSON.stringify({ continue: true }));
    return;
  }

  let hookInput = {};
  try {
    let input = "";
    for await (const chunk of process.stdin) {
      input += chunk;
    }
    if (input) {
      hookInput = JSON.parse(input);
    }
  } catch {
    /* ignore */
  }

  if (hookInput.cwd) {
    process.env.SADDLE_CWD = hookInput.cwd;
  }

  try {
    const ok = await getHealth();
    if (!ok) {
      process.stdout.write(
        JSON.stringify({
          continue: true,
          systemMessage:
            "Saddle: `saddle serve` does not appear reachable. Start it in the project (python -m saddle serve).",
        }),
      );
      return;
    }

    const data = await getRecentMemories(10);
    const total = data?.data?.total_count ?? data?.data?.count ?? 0;
    const episodes = data?.data?.episodes ?? [];
    const preview = episodes[0]?.content
      ? String(episodes[0].content).slice(0, 120)
      : "";

    const msg =
      total > 0
        ? `Saddle: ${total} memory row(s) for this workspace.${preview ? ` Latest: ${preview}${preview.length >= 120 ? "…" : ""}` : ""}`
        : "Saddle: no memories yet for this workspace; they will be stored after each assistant reply.";

    process.stdout.write(JSON.stringify({ continue: true, systemMessage: msg }));
  } catch {
    process.stdout.write(
      JSON.stringify({
        continue: true,
        systemMessage: "Saddle: could not query memory API (is saddle serve running on SADDLE_BASE_URL?)",
      }),
    );
  }
}

main();

import { test } from "node:test";
import assert from "node:assert/strict";
import { resolveConfig } from "../src/config.js";
import { searchMemories, saveMemories } from "../src/api.js";

test("resolveConfig uses defaults", () => {
  const c = resolveConfig({});
  assert.equal(c.serverUrl, "http://127.0.0.1:1995");
  assert.equal(c.groupId, "saddle-default-group");
});

test("searchMemories posts Saddle search body and maps response", async (t) => {
  const calls = [];
  globalThis.fetch = async (url, opts) => {
    calls.push({ url: String(url), body: opts.body ? JSON.parse(opts.body) : null });
    return {
      ok: true,
      status: 200,
      json: async () => ({
        data: {
          memories: [
            {
              memory_type: "episodic_memory",
              content: "hello",
              score: 0.85,
              timestamp: 1_700_000_000_000,
            },
          ],
          count: 1,
        },
      }),
    };
  };
  t.after(() => {
    delete globalThis.fetch;
  });

  const cfg = resolveConfig({ baseUrl: "http://127.0.0.1:1995", groupId: "g" });
  const out = await searchMemories(
    cfg,
    { query: "hi", top_k: 3, group_id: "g", memory_types: ["episodic_memory"] },
    { info: () => {}, warn: () => {} },
  );

  assert.equal(out.status, "ok");
  assert.equal(out.result.memories.length, 1);
  assert.equal(calls.length, 1);
  assert.match(calls[0].url, /\/api\/v1\/memories\/search$/);
  assert.equal(calls[0].body.query, "hi");
  assert.deepEqual(calls[0].body.filters, { group_id: "g" });
});

test("saveMemories posts batch GroupPayload", async (t) => {
  const calls = [];
  globalThis.fetch = async (url, opts) => {
    calls.push({ url: String(url), body: JSON.parse(opts.body) });
    return { ok: true, status: 200, json: async () => ({ status: "queued", count: 2 }) };
  };
  t.after(() => {
    delete globalThis.fetch;
  });

  const cfg = resolveConfig({});
  await saveMemories(cfg, {
    userId: "u",
    groupId: "g",
    messages: [
      { role: "user", content: "a" },
      { role: "assistant", content: "b" },
    ],
  });

  assert.equal(calls.length, 1);
  assert.match(calls[0].url, /\/api\/v1\/memories$/);
  assert.equal(calls[0].body.group_id, "g");
  assert.equal(calls[0].body.user_id, "u");
  assert.equal(calls[0].body.messages.length, 2);
});

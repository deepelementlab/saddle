import { test } from "node:test";
import assert from "node:assert/strict";
import { searchMemories, transformSearchResults, appendMessages } from "../hooks/scripts/utils/saddle-api.js";

test("transformSearchResults maps data.memories", () => {
  const out = transformSearchResults({
    data: {
      memories: [
        { content: "x", score: 0.9, timestamp: 1700000000000 },
      ],
    },
  });
  assert.equal(out.length, 1);
  assert.equal(out[0].text, "x");
  assert.equal(out[0].score, 0.9);
});

test("searchMemories POSTs and returns JSON", async (t) => {
  globalThis.fetch = async (url, opts) => {
    assert.match(url, /\/api\/v1\/memories\/search$/);
    const body = JSON.parse(opts.body);
    assert.equal(body.query, "q");
    assert.equal(body.filters.group_id, "claude-code:/tmp");
    return {
      ok: true,
      json: async () => ({ data: { memories: [], count: 0 } }),
    };
  };
  t.after(() => {
    delete globalThis.fetch;
  });

  process.env.SADDLE_CWD = "/tmp";
  delete process.env.SADDLE_GROUP_ID;

  const j = await searchMemories("q", { topK: 5 });
  assert.deepEqual(j.data.memories, []);
});

test("appendMessages POSTs GroupPayload", async (t) => {
  globalThis.fetch = async (url, opts) => {
    assert.match(url, /\/api\/v1\/memories$/);
    const body = JSON.parse(opts.body);
    assert.equal(body.group_id, "g");
    assert.equal(body.user_id, "u");
    assert.equal(body.messages.length, 1);
    return { ok: true, json: async () => ({ status: "queued" }) };
  };
  t.after(() => {
    delete globalThis.fetch;
  });

  process.env.SADDLE_GROUP_ID = "g";
  process.env.SADDLE_USER_ID = "u";

  await appendMessages([{ role: "user", content: "hi" }]);
});

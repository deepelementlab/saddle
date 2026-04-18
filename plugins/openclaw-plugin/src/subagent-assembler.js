/**
 * Context assembly from Saddle Memory API search results.
 */

import { searchMemories } from "./api.js";
import { buildMemoryPrompt, parseSearchResponse } from "./prompt.js";

/**
 * @typedef {import("./types.js").SaddleConfig} SaddleConfig
 */

export class ContextAssembler {
  /**
   * @param {SaddleConfig} cfg
   * @param {import("./types.js").Logger} logger
   */
  constructor(cfg, logger) {
    this.cfg = cfg;
    this.log = logger;
  }

  /**
   * @param {string} query
   * @param {Array} messages
   * @param {number} turnCount
   * @returns {Promise<{context: string, memoryCount: number}>}
   */
  async assemble(query, messages, turnCount) {
    const earlyTurnMultiplier = turnCount <= 2 ? 2 : 1;
    const topK = Math.min(this.cfg.topK * earlyTurnMultiplier, 20);

    const params = {
      query,
      user_id: this.cfg.userId,
      group_id: this.cfg.groupId || undefined,
      memory_types: this.cfg.memoryTypes,
      retrieve_method: this.cfg.retrieveMethod,
      top_k: topK,
    };

    const result = await searchMemories(this.cfg, params, this.log);
    const parsed = parseSearchResponse(result) || { episodic: [], pending: [] };

    const memoryCount =
      (parsed.episodic?.length || 0) + (parsed.pending?.length || 0);

    const context = buildMemoryPrompt(parsed, { wrapInCodeBlock: true });

    return { context, memoryCount };
  }
}

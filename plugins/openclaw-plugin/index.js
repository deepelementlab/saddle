import { createContextEngine } from "./src/engine.js";
import meta from "./openclaw.plugin.json" with { type: "json" };

export default function register(api) {
  const logger = api.logger || console;
  logger.info?.(`[${meta.id}] register context-engine`);
  api.registerContextEngine(meta.id, (pluginConfig) => createContextEngine(meta, pluginConfig, logger));
}

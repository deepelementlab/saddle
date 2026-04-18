const DEFAULT_URL = "http://127.0.0.1:1995";

export const TIMEOUT_MS = 60000;

export function resolveConfig(pc = {}) {
  return {
    serverUrl: (pc.baseUrl || DEFAULT_URL).replace(/\/*$/, ""),
    userId: pc.userId || "saddle-user",
    groupId: pc.groupId || "saddle-default-group",
    topK: pc.topK ?? 5,
    memoryTypes: pc.memoryTypes ?? ["episodic_memory"],
    retrieveMethod: pc.retrieveMethod ?? "hybrid",
  };
}

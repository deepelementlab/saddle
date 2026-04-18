const PREFIX = process.env.SADDLE_DEBUG === "1" ? "[saddle-hook]" : null;

export function setDebugPrefix() {}

export function debug(...args) {
  if (PREFIX) {
    console.error(PREFIX, ...args);
  }
}

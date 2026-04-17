import type { ModeConfig, ValidationResult } from "../types/mode";

const API_BASE = "/api/v1/modes";

async function parseJson<T>(resp: Response): Promise<T> {
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(text || `Request failed: ${resp.status}`);
  }
  return (await resp.json()) as T;
}

export async function listModes(): Promise<string[]> {
  const resp = await fetch(`${API_BASE}`);
  const data = await parseJson<{ modes: string[] }>(resp);
  return data.modes;
}

export async function showMode(name: string): Promise<ModeConfig> {
  const resp = await fetch(`${API_BASE}/${encodeURIComponent(name)}`);
  return parseJson<ModeConfig>(resp);
}

export async function validateMode(mode: ModeConfig): Promise<ValidationResult> {
  const resp = await fetch(`${API_BASE}/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(mode),
  });
  return parseJson<ValidationResult>(resp);
}

export async function saveMode(mode: ModeConfig): Promise<{ saved: string; mode: string }> {
  const resp = await fetch(`${API_BASE}/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(mode),
  });
  return parseJson<{ saved: string; mode: string }>(resp);
}

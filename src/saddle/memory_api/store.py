"""Local memory store for Saddle plugins."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any


class MemoryStore:
    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.file = self.root / "memories.jsonl"
        if not self.file.exists():
            self.file.write_text("", encoding="utf-8")

    def append_messages(self, group_id: str, user_id: str, messages: list[dict[str, Any]]) -> dict[str, Any]:
        now = int(time.time() * 1000)
        rows = []
        for m in messages:
            rows.append(
                {
                    "id": str(uuid.uuid4()),
                    "group_id": group_id,
                    "user_id": user_id,
                    "role": str(m.get("role") or "user"),
                    "content": str(m.get("content") or ""),
                    "timestamp": int(m.get("timestamp") or now),
                    "memory_type": "episodic_memory",
                }
            )
        with self.file.open("a", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return {"status": "queued", "count": len(rows), "request_id": str(uuid.uuid4())}

    def _all(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for line in self.file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
        return out

    def search(self, query: str, group_id: str | None, top_k: int = 5) -> list[dict[str, Any]]:
        q = query.lower().strip()
        items = self._all()
        if group_id:
            items = [x for x in items if x.get("group_id") == group_id]
        scored: list[tuple[int, dict[str, Any]]] = []
        for it in items:
            content = str(it.get("content") or "")
            score = content.lower().count(q) if q else 0
            if score > 0 or (q and any(tok in content.lower() for tok in q.split())):
                scored.append((max(score, 1), it))
        scored.sort(key=lambda x: (x[0], int(x[1].get("timestamp") or 0)), reverse=True)
        result = []
        for s, item in scored[:top_k]:
            cloned = dict(item)
            cloned["score"] = round(min(0.99, 0.6 + s * 0.1), 2)
            result.append(cloned)
        return result

    def get(self, group_id: str | None, page: int = 1, page_size: int = 50) -> dict[str, Any]:
        items = self._all()
        if group_id:
            items = [x for x in items if x.get("group_id") == group_id]
        items.sort(key=lambda x: int(x.get("timestamp") or 0), reverse=True)
        start = max(0, (page - 1) * page_size)
        end = start + page_size
        return {"episodes": items[start:end], "total_count": len(items), "count": len(items[start:end])}

"""Minimal slash router for Saddle commands."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SlashCommand:
    name: str
    description: str


BUILTIN_SLASH_COMMANDS = [
    SlashCommand("spec", "Specification workflow"),
    SlashCommand("clawteam", "Engineering team orchestration"),
    SlashCommand("designteam", "Product design orchestration"),
    SlashCommand("clawteam-deeploop-finalize", "Finalize clawteam deep-loop writeback"),
    SlashCommand("designteam-deeploop-finalize", "Finalize designteam deep-loop writeback"),
]


def parse_slash(input_text: str) -> tuple[str, str] | None:
    text = (input_text or "").strip()
    if not text.startswith("/"):
        return None
    body = text[1:]
    if not body:
        return None
    parts = body.split(maxsplit=1)
    name = parts[0].strip()
    rest = parts[1].strip() if len(parts) > 1 else ""
    return name, rest

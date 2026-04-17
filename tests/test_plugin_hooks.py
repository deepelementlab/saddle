from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

SADDLE_ROOT = Path(__file__).resolve().parents[1]
SRC = SADDLE_ROOT / "src"
HOOKS = SADDLE_ROOT / "plugins" / "claude-code-plugin" / "hooks" / "scripts"


def _free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = int(s.getsockname()[1])
    s.close()
    return port


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_claude_inject_memories_hook(tmp_path: Path) -> None:
    port = _free_port()
    memdir = tmp_path / "memapi"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    env["SADDLE_MEMORY_DIR"] = str(memdir)
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "saddle.memory_api.server:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=str(SADDLE_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(base + "/health", timeout=0.5)
                break
            except (urllib.error.URLError, OSError):
                time.sleep(0.1)
        else:
            pytest.fail("memory server did not start")

        req = urllib.request.Request(
            base + "/api/v1/memories/group",
            data=json.dumps(
                {
                    "group_id": "claude-code:/proj",
                    "user_id": "u",
                    "messages": [{"role": "user", "content": "dark mode preference"}],
                }
            ).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)

        hook_env = os.environ.copy()
        hook_env["SADDLE_BASE_URL"] = base
        r = subprocess.run(
            ["node", str(HOOKS / "inject-memories.js")],
            input=json.dumps({"prompt": "dark mode", "cwd": "/proj"}),
            capture_output=True,
            text=True,
            env=hook_env,
            cwd=str(SADDLE_ROOT),
            timeout=15,
            check=False,
        )
        assert r.returncode == 0, r.stderr
        out = json.loads(r.stdout)
        assert out.get("continue") is True
        assert "systemMessage" in out
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_claude_store_memories_hook(tmp_path: Path) -> None:
    port = _free_port()
    memdir = tmp_path / "memapi2"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    env["SADDLE_MEMORY_DIR"] = str(memdir)
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "saddle.memory_api.server:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=str(SADDLE_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    transcript = tmp_path / "t.jsonl"
    transcript.write_text(
        json.dumps(
            {"type": "user", "message": {"role": "user", "content": "hello saddle"}}
        )
        + "\n"
        + json.dumps(
            {
                "type": "assistant",
                "message": {"role": "assistant", "content": [{"type": "text", "text": "hi there"}]},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(base + "/health", timeout=0.5)
                break
            except (urllib.error.URLError, OSError):
                time.sleep(0.1)
        else:
            pytest.fail("memory server did not start")

        hook_env = os.environ.copy()
        hook_env["SADDLE_BASE_URL"] = base
        r = subprocess.run(
            ["node", str(HOOKS / "store-memories.js")],
            input=json.dumps({"transcript_path": str(transcript), "cwd": "/proj"}),
            capture_output=True,
            text=True,
            env=hook_env,
            cwd=str(SADDLE_ROOT),
            timeout=15,
            check=False,
        )
        assert r.returncode == 0, r.stderr
        out = json.loads(r.stdout)
        assert out.get("continue") is True
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

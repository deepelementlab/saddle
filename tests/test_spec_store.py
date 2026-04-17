from __future__ import annotations

from pathlib import Path

from saddle.spec.store import SpecBundle, SpecStore


def test_spec_store_roundtrip(tmp_path: Path) -> None:
    store = SpecStore(working_directory=str(tmp_path))
    bundle = SpecBundle(
        session_id="sess-abc-12345678",
        user_request="Build feature X",
        spec_markdown="# Spec\n",
        tasks_markdown="# Tasks\n",
        checklist_markdown="# Checklist\n",
        created_at=1700000000,
    )
    saved = store.save_bundle(bundle)
    assert saved.spec_dir
    loaded = store.load_bundle(saved.spec_dir)
    assert loaded is not None
    assert loaded.session_id == bundle.session_id
    assert loaded.user_request == bundle.user_request

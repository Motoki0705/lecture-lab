"""Protect originals, mirrored paths and reproducible import metadata."""

import json

import pytest

from src.common.library import Session, import_file


def test_import_preserves_original_and_is_idempotent(tmp_path):
    original = tmp_path / "original.pdf"
    original.write_bytes(b"one")
    session = Session(tmp_path / "repo", "2026_spring", "集積回路", "01")
    target = import_file(session, original, "slides")
    assert target.read_bytes() == original.read_bytes() == b"one"
    assert import_file(session, original, "slides") == target
    manifest = json.loads((session.processed / "sources.json").read_text())
    assert len(manifest["sources"]) == 1
    assert manifest["sources"][0]["raw_path"].endswith("/01/slides/original.pdf")
    original.write_bytes(b"different")
    with pytest.raises(FileExistsError):
        import_file(session, original, "slides")
    assert target.read_bytes() == b"one"


@pytest.mark.parametrize("value", ["..", "../elsewhere", "/tmp", "a/b", "a\\b", ""])
def test_session_rejects_escape(tmp_path, value):
    with pytest.raises(ValueError):
        Session(tmp_path, "2026_spring", value, "01")


def test_symlink_destination_cannot_escape(tmp_path):
    session = Session(tmp_path / "repo", "2026_spring", "集積回路", "01")
    session.raw.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    (session.raw / "audio").symlink_to(outside, target_is_directory=True)
    original = tmp_path / "recording.m4a"
    original.write_bytes(b"audio")
    with pytest.raises(ValueError):
        import_file(session, original, "audio")
    assert not list(outside.iterdir())

"""Interrupted runs must resume without presenting partial work as complete."""

import json
import subprocess
import sys
import wave
from dataclasses import dataclass
from pathlib import Path

import pytest

from src.common import pipeline
from src.common.library import Session, import_file


@dataclass
class Evidence:
    observed_model: str = "test-double"


@dataclass
class Result:
    output: dict
    evidence: Evidence


def test_resume_reuses_completed_parts_and_publishes_only_complete(tmp_path, monkeypatch):
    original = tmp_path / "source.wav"
    with wave.open(str(original), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(16000)
        stream.writeframes(b"\0\0" * 16000 * 3)
    session = Session(tmp_path / "repo", "2026_spring", "集積回路", "01")
    source = import_file(session, original, "audio")
    calls = []

    class FakeGemini:
        def __init__(self, root):
            pass

        def turn(self, prompt, schema, *, timeout, media_files):
            name = media_files[0].stem
            calls.append(name)
            if len(calls) == 2:
                raise RuntimeError("model disconnected")
            return Result({"markdown": f"内容{name}", "uncertainties": []}, Evidence())

    monkeypatch.setattr(pipeline, "Gemini", FakeGemini)
    with pytest.raises(RuntimeError, match="disconnected"):
        pipeline.transcribe(session, source, chunk_seconds=1)
    output = session.processed / "audio/source.wav"
    assert not (output / "transcript.md").exists()
    result = pipeline.transcribe(session, source, chunk_seconds=1)
    assert result["state"] == "complete"
    assert calls == ["part-0000", "part-0001", "part-0001", "part-0002"]
    assert (output / "transcript.md").read_text().count("内容") == 3
    assert pipeline.transcribe(session, source, chunk_seconds=1)["reused"] is True
    (output / "transcript.md").write_text("changed")
    with pytest.raises(ValueError, match="changed"):
        pipeline.transcribe(session, source, chunk_seconds=1)


def test_partial_budget_does_not_publish(tmp_path, monkeypatch):
    session = Session(tmp_path / "repo", "2026_spring", "集積回路", "01")
    pdf = tmp_path / "slides.pdf"
    writer = pipeline.PdfWriter()
    for _ in range(4):
        writer.add_blank_page(width=100, height=100)
    with pdf.open("wb") as stream:
        writer.write(stream)
    source = import_file(session, pdf, "slides")

    class FakeGemini:
        def __init__(self, root):
            pass

        def turn(self, *args, **kwargs):
            return Result({"markdown": "内容", "uncertainties": []}, Evidence())

    monkeypatch.setattr(pipeline, "Gemini", FakeGemini)
    result = pipeline.transcribe(session, source, limit_parts=1)
    assert result["state"] == "partial"
    assert result["total_parts"] == 2
    assert not list(session.processed.rglob("transcript.md"))


def test_media_hook_approves_only_supplied_file(tmp_path):
    schema = tmp_path / "schema.json"
    schema.write_text("{}")
    journal = tmp_path / "hooks.jsonl"
    journal.touch()
    media = tmp_path / "input.wav"
    media.write_bytes(b"audio")
    unrelated = tmp_path / "unrelated.txt"
    unrelated.write_text("private")
    hook = Path(__file__).resolve().parents[1] / ".agents/ops/explain_html/no_tools.py"
    from src.common.library import digest

    for target, expected in [(media, "auto_approve"), (unrelated, "deny")]:
        value = subprocess.check_output(
            [sys.executable, str(hook), str(journal), str(schema), digest(schema), str(media)],
            input=json.dumps({"toolCall": {"name": "read_file", "args": {"Path": str(target)}}}),
            text=True,
        )
        assert json.loads(value)["decision"] == expected

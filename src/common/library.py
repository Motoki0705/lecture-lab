"""Mirrored source storage, with explicit identities and collision protection."""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def component(value: str) -> str:
    if not value or value in {".", ".."} or any(c in value for c in "/\\\x00\n\r"):
        raise ValueError(f"Invalid path component: {value!r}")
    return value


def save_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temp.replace(path)


@dataclass(frozen=True)
class Session:
    root: Path
    term: str
    course: str
    lesson: str

    def __post_init__(self):
        for part in (self.term, self.course, self.lesson):
            component(part)

    @property
    def relative(self) -> Path:
        return Path(self.term, self.course, self.lesson)

    @property
    def raw(self) -> Path:
        return self.root / "data/raw" / self.relative

    @property
    def processed(self) -> Path:
        return self.root / "data/processed" / self.relative

    def create(self) -> None:
        for path in (self.raw, self.processed):
            if not path.resolve().is_relative_to(self.root.resolve()):
                raise ValueError("Session path escapes project")
            path.mkdir(parents=True, exist_ok=True)
            (path / ".gitkeep").touch(exist_ok=True)


def import_file(session: Session, source: Path, kind: str, *, note: str = "") -> Path:
    if kind not in {"audio", "slides", "materials"}:
        raise ValueError("kind must be audio, slides or materials")
    if not source.is_file():
        raise FileNotFoundError(source)
    session.create()
    target = session.raw / kind / source.name
    if not target.resolve().is_relative_to(session.raw.resolve()):
        raise ValueError("Source destination escapes raw session")
    sha = digest(source)
    manifest_path = session.processed / "sources.json"
    manifest = (
        json.loads(manifest_path.read_text())
        if manifest_path.exists()
        else {
            "term": session.term,
            "course": session.course,
            "lesson": session.lesson,
            "sources": [],
        }
    )
    relative = target.relative_to(session.root).as_posix()
    if target.exists() and digest(target) != sha:
        raise FileExistsError(f"Different content already exists: {target}")
    old = next((item for item in manifest["sources"] if item["raw_path"] == relative), None)
    if old is not None and old["sha256"] != sha:
        raise FileExistsError("Registered source changed; import under a new name")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        with target.open("xb") as output, source.open("rb") as input_stream:
            shutil.copyfileobj(input_stream, output)
    if digest(target) != sha:
        raise OSError(f"Copy verification failed: {target}")
    if old is None:
        manifest["sources"].append(
            {
                "kind": kind,
                "original_name": source.name,
                "raw_path": relative,
                "sha256": sha,
                "bytes": source.stat().st_size,
                "imported_at": datetime.now(UTC).isoformat(),
                "assignment_note": note,
            }
        )
        save_json(manifest_path, manifest)
    return target

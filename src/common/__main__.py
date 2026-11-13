"""Run from project root: .venv/bin/python -m src.common --help."""

import argparse
import json
from pathlib import Path

from .library import Session, import_file


def main():
    parser = argparse.ArgumentParser(description="授業資料の取り込み・文字起こし・学習資料作成")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--term", default="2026_spring")
    parser.add_argument("--course", required=True)
    parser.add_argument("--lesson", required=True, help="例: 01")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    ingest = commands.add_parser("import")
    ingest.add_argument("source", type=Path)
    ingest.add_argument("--kind", choices=["audio", "slides", "materials"], required=True)
    ingest.add_argument("--note", default="")
    transcript = commands.add_parser("transcribe")
    transcript.add_argument("source", type=Path)
    transcript.add_argument("--limit-parts", type=int)
    transcript.add_argument("--chunk-seconds", type=int, default=300)
    transcript.add_argument("--pages-per-part", type=int, default=3)
    transcript.add_argument("--timeout", type=int, default=600)
    author = commands.add_parser("draft")
    author.add_argument("--purpose", required=True)
    author.add_argument("--name", required=True)
    args = parser.parse_args()
    session = Session(args.root.resolve(), args.term, args.course, args.lesson)
    if args.command == "init":
        session.create()
        result = {"raw": str(session.raw), "processed": str(session.processed)}
    elif args.command == "import":
        result = {"path": str(import_file(session, args.source, args.kind, note=args.note))}
    else:
        from .pipeline import draft, transcribe

        if args.command == "transcribe":
            result = transcribe(
                session,
                args.source,
                limit_parts=args.limit_parts,
                chunk_seconds=args.chunk_seconds,
                pages_per_part=args.pages_per_part,
                timeout=args.timeout,
            )
        else:
            result = {"output": str(draft(session, args.purpose, args.name))}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

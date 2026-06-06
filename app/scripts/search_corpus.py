#!/usr/bin/env python3
"""Search the 红楼梦知识库 corpus with context snippets — fallback keyword search."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


DEFAULT_ROOT = Path(os.environ.get("HLM_KB_ROOT", "/Users/yue/Downloads/03_工程项目/读书工具/知识库"))
SEARCH_DIRS = (
    Path("raw") / "红楼梦",
    Path("books") / "红楼梦",
    Path("notes"),
    Path("topics"),
)
EXTS = {".txt", ".md", ".json"}


def iter_files(root: Path):
    for rel_dir in SEARCH_DIRS:
        base = root / rel_dir
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix.lower() in EXTS:
                yield path


def line_matches(line: str, terms: list[str], any_term: bool) -> bool:
    folded = line.casefold()
    hits = [term.casefold() in folded for term in terms]
    return any(hits) if any_term else all(hits)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("terms", nargs="+", help="terms to search; default requires all terms on one line")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--any", action="store_true", help="match any term instead of all terms")
    parser.add_argument("--context", type=int, default=2, help="context lines around each hit")
    parser.add_argument("--limit", type=int, default=80, help="maximum hits to print")
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    shown = 0
    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = text.split("\n")
        matched = False
        for i, line in enumerate(lines):
            if line_matches(line, args.terms, args.any):
                if not matched:
                    rel = path.relative_to(root)
                    print(f"\n=== {rel} ===")
                    matched = True
                    shown += 1
                start = max(0, i - args.context)
                end = min(len(lines), i + args.context + 1)
                print(f"  --- lines {start+1}-{end} ---")
                for j in range(start, end):
                    marker = ">" if j == i else " "
                    print(f"  {marker} {lines[j]}")
                print()
                if shown >= args.limit:
                    return


if __name__ == "__main__":
    main()

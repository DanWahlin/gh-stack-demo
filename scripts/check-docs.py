#!/usr/bin/env python3
"""Check local Markdown links, fences, and list punctuation."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_TARGET = re.compile(r"!?\[[^]]*]\(([^)]+)\)")
HTML_SOURCE = re.compile(r'<(?:img|source)\b[^>]*\bsrc="([^"]+)"')
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+(.*)$")


def markdown_files() -> list[Path]:
    ignored = {".git", "node_modules"}
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if not any(part in ignored for part in path.parts)
    )


def main() -> int:
    failures: list[str] = []
    files = markdown_files()

    for path in files:
        text = path.read_text(encoding="utf-8")
        if text.count("```") % 2:
            failures.append(f"{path.relative_to(ROOT)} has unbalanced code fences")

        in_fence = False
        for line_number, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            match = LIST_ITEM.match(line)
            if not match or not match.group(1).endswith("."):
                continue
            visible = re.sub(r"\]\([^)]+\)", "]", match.group(1))
            visible = re.sub(r"`[^`]+`", "CODE", visible)
            if not re.search(r"\.\s+\S", visible[:-1]):
                failures.append(
                    f"{path.relative_to(ROOT)}:{line_number} has a terminal period "
                    "on a single-sentence list item"
                )

        targets = MARKDOWN_TARGET.findall(text) + HTML_SOURCE.findall(text)
        for target in targets:
            target = target.strip().split(maxsplit=1)[0]
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = unquote(target.split("#", 1)[0])
            if not relative:
                continue
            resolved = (path.parent / relative).resolve()
            if ROOT not in resolved.parents and resolved != ROOT:
                failures.append(
                    f"{path.relative_to(ROOT)} links outside the repository: {target}"
                )
            elif not resolved.exists():
                failures.append(
                    f"{path.relative_to(ROOT)} has a missing link target: {target}"
                )

    if failures:
        print("Documentation checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Documentation checks passed for {len(files)} Markdown files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

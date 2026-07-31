#!/usr/bin/env python3
"""Verify that documented gh stack commands and flags exist in the installed CLI."""

from __future__ import annotations

import subprocess
import sys


CONTRACTS = [
    (["gh", "stack", "init", "--help"], ["--base", "bottom to top"]),
    (["gh", "stack", "add", "--help"], ["Add a new branch on top"]),
    (["gh", "stack", "view", "--help"], ["--json"]),
    (["gh", "stack", "up", "--help"], ["further up in the stack"]),
    (["gh", "stack", "down", "--help"], ["further down in the stack"]),
    (["gh", "stack", "top", "--help"], ["top branch of the stack"]),
    (["gh", "stack", "bottom", "--help"], ["bottom branch of the stack"]),
    (["gh", "stack", "trunk", "--help"], ["trunk branch of the current stack"]),
    (
        ["gh", "stack", "submit", "--help"],
        ["--auto", "--open", "created as drafts unless you pass"],
    ),
    (["gh", "stack", "push", "--help"], ["force-with-lease"]),
    (["gh", "stack", "sync", "--help"], ["--prune", "diverged", "non-interactive"]),
    (
        ["gh", "stack", "rebase", "--help"],
        ["--abort", "--continue"],
    ),
    (
        ["gh", "stack", "merge", "--help"],
        ["--yes", "--squash", "--merge-method"],
    ),
]


def run(command: list[str]) -> str:
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    output = f"{result.stdout}\n{result.stderr}"
    if result.returncode != 0:
        raise RuntimeError(
            f"{' '.join(command)} exited with {result.returncode}:\n{output.strip()}"
        )
    return output


def main() -> int:
    version = run(["gh", "stack", "--version"]).strip()
    failures: list[str] = []

    for command, required_fragments in CONTRACTS:
        output = run(command)
        for fragment in required_fragments:
            if fragment not in output:
                failures.append(f"{' '.join(command)} is missing {fragment!r}")

    print(f"CLI: {version}")
    if failures:
        print("gh stack documentation contract failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"gh stack help contract passed for {len(CONTRACTS)} commands.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

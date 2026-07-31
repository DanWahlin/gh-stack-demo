#!/usr/bin/env python3
"""Verify the public stacked-PR training artifact through GitHub CLI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

EXPECTED = [
    {
        "base": "main",
        "head": "training/task-model",
        "files": ["src/tasks.js"],
    },
    {
        "base": "training/task-model",
        "head": "training/task-validation",
        "files": ["src/tasks.js"],
    },
    {
        "base": "training/task-validation",
        "head": "training/task-tests",
        "files": ["test/tasks.test.js"],
    },
]


def run(*args: str) -> str:
    result = subprocess.run(args, check=False, text=True, capture_output=True)
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"{' '.join(args)} failed: {detail}")
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo",
        default="DanWahlin/gh-stacked-prs-demo",
        help="GitHub repository containing the canonical open stack",
    )
    args = parser.parse_args()

    failures: list[str] = []

    try:
        version = run("gh", "stack", "--version").strip()
        view_help = run("gh", "stack", "view", "--help")
        submit_help = run("gh", "stack", "submit", "--help")
    except RuntimeError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    if "--json" not in view_help:
        failures.append("gh stack view no longer documents --json")
    if "--auto" not in submit_help or "--open" not in submit_help:
        failures.append("gh stack submit no longer documents --auto and --open")

    print(f"CLI: {version}")
    print(f"Repository: https://github.com/{args.repo}")

    for expected in EXPECTED:
        try:
            raw = run(
                "gh",
                "pr",
                "list",
                "--repo",
                args.repo,
                "--state",
                "open",
                "--head",
                expected["head"],
                "--json",
                "number,state,isDraft,baseRefName,headRefName,files,url",
            )
            matches = json.loads(raw)
        except (RuntimeError, json.JSONDecodeError) as error:
            failures.append(f"{expected['head']} could not be inspected: {error}")
            continue

        if len(matches) != 1:
            failures.append(
                f"{expected['head']}: expected one open PR, observed {len(matches)}"
            )
            continue

        pr = matches[0]
        actual_files = sorted(item["path"] for item in pr["files"])
        expected_files = sorted(expected["files"])
        checks = {
            "state": (pr["state"], "OPEN"),
            "draft": (pr["isDraft"], False),
            "base": (pr["baseRefName"], expected["base"]),
            "head": (pr["headRefName"], expected["head"]),
            "files": (actual_files, expected_files),
        }
        for label, (actual, wanted) in checks.items():
            if actual != wanted:
                failures.append(
                    f"PR #{pr['number']} {label}: expected {wanted!r}, observed {actual!r}"
                )

        print(
            f"PR #{pr['number']}: {pr['baseRefName']} <- {pr['headRefName']} "
            f"({', '.join(actual_files)})"
        )

    if failures:
        print("\nDemo integrity check failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("\nDemo integrity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

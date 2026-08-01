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
        "head": "tasks/model",
        "position": 1,
        "files": ["src/tasks.js", "test/tasks.model.test.js"],
    },
    {
        "base": "tasks/model",
        "head": "tasks/validation",
        "position": 2,
        "files": ["src/tasks.js", "test/tasks.validation.test.js"],
    },
    {
        "base": "tasks/validation",
        "head": "tasks/api",
        "position": 3,
        "files": ["package.json", "src/server.js", "test/tasks.api.test.js"],
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
        default="DanWahlin/learn-github-stacked-prs",
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
    observed_stack_ids: set[int] = set()

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

        try:
            pull = json.loads(
                run(
                    "gh",
                    "api",
                    "-H",
                    "X-GitHub-Api-Version: 2026-03-10",
                    f"repos/{args.repo}/pulls/{pr['number']}",
                )
            )
            stack = pull.get("stack")
        except (RuntimeError, json.JSONDecodeError) as error:
            failures.append(f"PR #{pr['number']} stack could not be inspected: {error}")
            stack = None

        stack_detail = ""
        if stack is None:
            failures.append(f"PR #{pr['number']} is not linked to a GitHub stack")
        else:
            observed_stack_ids.add(stack["id"])
            stack_detail = (
                f"; stack #{stack['number']} position "
                f"{stack['position']}/{stack['size']}"
            )
            stack_checks = {
                "stack position": (stack["position"], expected["position"]),
                "stack size": (stack["size"], len(EXPECTED)),
                "stack base": (stack["base"]["ref"], "main"),
            }
            for label, (actual, wanted) in stack_checks.items():
                if actual != wanted:
                    failures.append(
                        f"PR #{pr['number']} {label}: expected {wanted!r}, "
                        f"observed {actual!r}"
                    )

        print(
            f"PR #{pr['number']}: {pr['baseRefName']} <- {pr['headRefName']} "
            f"({', '.join(actual_files)}){stack_detail}"
        )

    if len(observed_stack_ids) != 1:
        failures.append(
            "expected all canonical pull requests to share one GitHub stack, "
            f"observed stack IDs {sorted(observed_stack_ids)}"
        )

    if failures:
        print("\nTraining stack integrity check failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("\nTraining stack integrity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

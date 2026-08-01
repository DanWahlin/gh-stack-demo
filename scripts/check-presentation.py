#!/usr/bin/env python3
"""Verify the PowerPoint's learner-facing content and hyperlink contract."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "github-stacked-prs.pptx"

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
RID = f"{{{NS['r']}}}id"

REQUIRED_TEXT = [
    "Git 2.20 or newer",
    "Node.js 20 or newer",
    "GitHub CLI 2.90 or newer",
    "Git identity + GitHub push access",
    "INTERACTIVE HUMAN WORKFLOW",
    "gh extension install github/gh-stack",
    "gh skill install github/gh-stack gh-stack",
    "gh stack init --base main tasks/model",
    "gh stack add tasks/validation",
    "gh stack add tasks/api",
    "gh stack view --json",
    "gh stack submit --auto --open",
    "gh stack sync",
    "gh stack merge --yes --squash",
    "github.com/DanWahlin/learn-github-stacked-prs",
]
FORBIDDEN_TEXT = [
    "Stacked PRs available",
    "Command success ≠ verification",
]
EXPECTED_TIMING_SLIDES = {
    "ppt/slides/slide2.xml",
    "ppt/slides/slide3.xml",
    "ppt/slides/slide4.xml",
}


def slide_order(archive: zipfile.ZipFile) -> list[str]:
    presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
    relationships = ET.fromstring(
        archive.read("ppt/_rels/presentation.xml.rels")
    )
    targets = {
        relationship.attrib["Id"]: relationship.attrib["Target"]
        for relationship in relationships
    }
    slide_list = presentation.find("p:sldIdLst", NS)
    if slide_list is None:
        return []
    return [
        "ppt/" + targets[slide.attrib[RID]]
        for slide in slide_list
    ]


def relationship_targets(archive: zipfile.ZipFile, slide_name: str) -> dict[str, str]:
    slide_path = Path(slide_name)
    rels_name = str(
        slide_path.parent / "_rels" / f"{slide_path.name}.rels"
    )
    relationships = ET.fromstring(archive.read(rels_name))
    return {
        relationship.attrib["Id"]: relationship.attrib["Target"]
        for relationship in relationships
    }


def main() -> int:
    failures: list[str] = []

    try:
        archive = zipfile.ZipFile(DECK)
        bad_member = archive.testzip()
    except (OSError, zipfile.BadZipFile) as error:
        print(f"Presentation check failed: {error}", file=sys.stderr)
        return 1

    with archive:
        if bad_member:
            failures.append(f"corrupt ZIP member: {bad_member}")

        slides = slide_order(archive)
        if len(slides) != 7:
            failures.append(f"expected 7 slides, observed {len(slides)}")

        roots = {name: ET.fromstring(archive.read(name)) for name in slides}
        slide_text = {
            name: " | ".join(
                node.text or "" for node in root.findall(".//a:t", NS)
            )
            for name, root in roots.items()
        }
        all_text = "\n".join(slide_text.values())

        for required in REQUIRED_TEXT:
            if required not in all_text:
                failures.append(f"missing required presentation text: {required!r}")
        for forbidden in FORBIDDEN_TEXT:
            if forbidden in all_text:
                failures.append(f"stale presentation text remains: {forbidden!r}")
        if all_text.count("run npm test") < 3:
            failures.append("the final workflow must test all three layers")

        timing_slides = {
            name for name, root in roots.items() if root.find("p:timing", NS) is not None
        }
        if timing_slides != EXPECTED_TIMING_SLIDES:
            failures.append(
                "animation timing moved or disappeared: "
                f"expected {sorted(EXPECTED_TIMING_SLIDES)}, "
                f"observed {sorted(timing_slides)}"
            )

        run_hyperlinks = sum(
            len(root.findall(".//a:rPr/a:hlinkClick", NS)) for root in roots.values()
        )
        if run_hyperlinks:
            failures.append(
                f"found {run_hyperlinks} text-run hyperlinks; use shape-level links "
                "to prevent visible underlines"
            )

        for name, root in roots.items():
            targets = relationship_targets(archive, name)
            badge_shapes = [
                shape
                for shape in root.findall(".//p:sp", NS)
                if "gh.io/stacks"
                in "".join(node.text or "" for node in shape.findall(".//a:t", NS))
            ]
            if len(badge_shapes) != 1:
                failures.append(
                    f"{name}: expected one gh.io/stacks badge, observed {len(badge_shapes)}"
                )
                continue
            clicks = badge_shapes[0].findall("./p:nvSpPr/p:cNvPr/a:hlinkClick", NS)
            if len(clicks) != 1 or targets.get(clicks[0].attrib[RID]) != "https://gh.io/stacks":
                failures.append(f"{name}: gh.io/stacks badge is not linked correctly")

        # The visible repository labels on the title and final slides must remain clickable.
        for name in (slides[0], slides[-1]):
            root = roots[name]
            targets = relationship_targets(archive, name)
            repo_shapes = [
                shape
                for shape in root.findall(".//p:sp", NS)
                if "learn-github-stacked-prs"
                in "".join(node.text or "" for node in shape.findall(".//a:t", NS))
            ]
            if len(repo_shapes) != 1:
                failures.append(
                    f"{name}: expected one visible repository link, observed {len(repo_shapes)}"
                )
                continue
            clicks = repo_shapes[0].findall("./p:nvSpPr/p:cNvPr/a:hlinkClick", NS)
            expected = "https://github.com/DanWahlin/learn-github-stacked-prs"
            if len(clicks) != 1 or targets.get(clicks[0].attrib[RID]) != expected:
                failures.append(f"{name}: visible repository label is not linked correctly")

    if failures:
        print("Presentation contract failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Presentation contract passed for 7 slides.")
    print("- Official prerequisites are present.")
    print("- Core CLI workflow and per-layer tests are present.")
    print("- Animations and shape-level hyperlinks are intact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

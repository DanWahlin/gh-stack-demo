# Slide deck source

Dan's PowerPoint is the source of truth. The current foundation is stored in `github-stacked-prs-animated-base.pptx`; the generated working deck is `github-stacked-prs.pptx`.

The deck contains:

1. Getting Started with GitHub Stacked PRs
2. The dilemma: giant PR versus serial small PRs
3. The solution: dependent development with focused reviews
4. The high-level workflow
5. A copyable terminal example that creates three stacked PRs

Slides 2–4 include Dan's PowerPoint animations. Future changes must start from `github-stacked-prs-animated-base.pptx` and use targeted OOXML edits so those animations are preserved. Do not regenerate the full deck from the old HTML slide sources.

## Current build

```sh
npm install --no-save --no-package-lock pptxgenjs playwright sharp
NODE_PATH="$PWD/node_modules" node slides/render-logo.cjs
NODE_PATH="$PWD/node_modules" node slides/build-real-workflow.cjs
python slides/append-real-workflow.py
```

`append-real-workflow.py`:

- Changes only the command text `gh stack rebase` to `gh stack sync` on the high-level workflow slide while retaining its animation tree.
- Appends the real terminal workflow as slide 5.
- Leaves slides 1–3 byte-for-byte unchanged.

Every slide includes a clickable `gh.io/stacks` badge and GitHub's Invertocat mark.

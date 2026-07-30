# Slide deck source

The current presentation is based on Dan's animated PowerPoint, stored as `github-stacked-prs-animated-base.pptx`. That file is the source of truth for the three animated content slides.

The final deck adds a title slide before the animated slides:

1. Getting Started with GitHub Stacked PRs
2. The dilemma: giant PR versus serial small PRs
3. The solution: dependent development with focused reviews
4. The workflow: create, submit, review, and merge

Every slide includes a clickable `gh.io/stacks` badge and GitHub's Invertocat mark.

## Build

```sh
npm install --no-save --no-package-lock pptxgenjs playwright sharp
NODE_PATH="$PWD/node_modules" node slides/render-logo.cjs
NODE_PATH="$PWD/node_modules" node slides/build-title.cjs
python slides/add-title-to-animated.py
```

The build produces `github-stacked-prs.pptx` in the repository root. The merge script imports the title slide without rewriting the existing content-slide XML, preserving Dan's PowerPoint animations.

The Invertocat source is fetched from the official GitHub Stacked PRs documentation site and rendered white for the dark slide background.

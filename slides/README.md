# Slide deck source

Three GitHub-inspired visuals for the accompanying sub-three-minute video:

1. The dilemma: giant PR versus serial small PRs
2. The solution: dependent development with focused reviews
3. The workflow: create, submit, review, and merge

Every slide includes a clickable `gh.io/stacks` badge and GitHub's Invertocat mark.

## Build

```sh
npm install --no-save --no-package-lock pptxgenjs playwright sharp
NODE_PATH="$PWD/node_modules" node slides/render-logo.cjs
NODE_PATH="$PWD/node_modules" node slides/build.cjs
```

The build produces `github-stacked-prs.pptx` in the repository root.

The Invertocat source is fetched from the official GitHub Stacked PRs documentation site and rendered white for the dark slide background.

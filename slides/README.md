# Slide deck source

Three GitHub-inspired visuals for the accompanying sub-three-minute video:

1. The dilemma: giant PR versus serial small PRs
2. The solution: dependent development with focused reviews
3. The workflow: create, submit, review, and merge

## Build

```sh
npm install --no-save --no-package-lock pptxgenjs playwright sharp
NODE_PATH="$PWD/node_modules" node slides/build.cjs
```

The build produces `github-stacked-prs.pptx` in the repository root.

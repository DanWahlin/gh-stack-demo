# Contributing

Contributions that improve the stacked pull request training experience are welcome.

## Before making changes

1. Read [`AGENTS.md`](AGENTS.md).
2. Decide whether the work needs a normal pull request, one stack, or separate stacks.
3. Open an issue or discussion before changing the canonical workshop structure or public live-stack contract.
4. Do not modify, merge, or close the public validation pull requests.

## Validate documentation changes

Run:

```sh
python scripts/check-docs.py
python scripts/verify-demo.py
```

## Validate code examples

Run the tests from the top branch of a disposable or validation stack. Confirm that every pull request still contains only its intended layer.

## Pull request expectations

Describe:

- The learner or facilitator problem being solved
- The files and training path affected
- Commands used for verification
- Screenshots when GitHub UI behavior changes
- Any `gh-stack` version assumptions

Keep documentation examples concise, executable, and consistent with current `gh stack --help` output.

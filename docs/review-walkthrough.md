# Review the live stack

Use the open training stack in [this repository](https://github.com/DanWahlin/gh-stacked-prs/pulls) for this walkthrough.

## Stack graph

```text
main
└── workshop/task-model
    └── workshop/task-validation
        └── workshop/task-tests
```

## Bottom PR: Task model

Open the pull request whose head branch is [`workshop/task-model`](https://github.com/DanWahlin/gh-stacked-prs/pulls?q=is%3Apr+head%3Aworkshop%2Ftask-model).

Verify:

- Base: `main`
- Head: `workshop/task-model`
- Changed file: `src/tasks.js`
- Responsibility: Create a task with an ID, title, and incomplete state

Review the domain shape before reviewing dependent validation or tests. A design change requested here affects every layer above it.

Sample review question:

> Should task creation normalize the title, or should normalization belong in the validation layer?

The team must answer this boundary question before approving higher layers.

## Middle PR: Validation

Open the pull request whose head branch is [`workshop/task-validation`](https://github.com/DanWahlin/gh-stacked-prs/pulls?q=is%3Apr+head%3Aworkshop%2Ftask-validation).

Verify:

- Base: `workshop/task-model`
- Head: `workshop/task-validation`
- Changed file: `src/tasks.js`
- Responsibility: Validate missing or whitespace-only task titles

The Files changed tab shows only the validation addition because the PR targets the model branch instead of `main`.

Sample review question:

> Does validation return enough information for callers, or is a Boolean appropriate for this layer?

## Top PR: Tests

Open the pull request whose head branch is [`workshop/task-tests`](https://github.com/DanWahlin/gh-stacked-prs/pulls?q=is%3Apr+head%3Aworkshop%2Ftask-tests).

Verify:

- Base: `workshop/task-validation`
- Head: `workshop/task-tests`
- Changed file: `test/tasks.test.js`
- Responsibility: Verify task creation and whitespace validation

Sample review question:

> Which behavior is still untested, and does that missing case belong in this layer or a lower one?

## Review sequence

1. Review the model PR and resolve foundational design questions.
2. Review the validation PR against the approved model contract.
3. Review the tests PR against the behavior introduced below it.
4. Confirm that all checks pass.
5. Merge only the approved portion of the stack.

## What a poor stack looks like

Stop and restructure when:

- A PR contains several unrelated responsibilities.
- A higher layer can be reviewed without the lower layer and therefore belongs in a separate stack.
- Tests exist only at the top even though lower layers can fail independently.
- Formatting or generated-file churn hides the functional change.
- Reviewers cannot state the acceptance criterion for one layer.

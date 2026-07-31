# Review the live stack

Use the independently generated [validation repository](https://github.com/DanWahlin/gh-stack-demo-validated) for this walkthrough.

## Stack graph

```text
main
└── PR #1: feature/task-model
    └── PR #2: feature/task-validation
        └── PR #3: test/task-model
```

## PR #1: Task model

Open [PR #1](https://github.com/DanWahlin/gh-stack-demo-validated/pull/1).

Verify:

- Base: `main`
- Head: `feature/task-model`
- Changed file: `src/tasks.js`
- Responsibility: Create a task with an ID, title, and incomplete state

Review the domain shape before reviewing dependent validation or tests. A design change requested here affects every layer above it.

Sample review question:

> Should task creation normalize the title, or should normalization belong in the validation layer?

The team must answer this boundary question before approving higher layers.

## PR #2: Validation

Open [PR #2](https://github.com/DanWahlin/gh-stack-demo-validated/pull/2).

Verify:

- Base: `feature/task-model`
- Head: `feature/task-validation`
- Changed file: `src/tasks.js`
- Responsibility: Validate missing or whitespace-only task titles

The Files changed tab shows only the validation addition because the PR targets the model branch instead of `main`.

Sample review question:

> Does validation return enough information for callers, or is a Boolean appropriate for this layer?

## PR #3: Tests

Open [PR #3](https://github.com/DanWahlin/gh-stack-demo-validated/pull/3).

Verify:

- Base: `feature/task-validation`
- Head: `test/task-model`
- Changed file: `test/tasks.test.js`
- Responsibility: Verify task creation and whitespace validation

Sample review question:

> Which behavior is still untested, and does that missing case belong in this layer or a lower one?

## Review sequence

1. Review PR #1 and resolve foundational design questions.
2. Review PR #2 against the approved model contract.
3. Review PR #3 against the behavior introduced below it.
4. Confirm that all checks pass.
5. Merge only the approved portion of the stack.

## What a poor stack looks like

Stop and restructure when:

- A PR contains several unrelated responsibilities.
- A higher layer can be reviewed without the lower layer and therefore belongs in a separate stack.
- Tests exist only at the top even though lower layers can fail independently.
- Formatting or generated-file churn hides the functional change.
- Reviewers cannot state the acceptance criterion for one layer.

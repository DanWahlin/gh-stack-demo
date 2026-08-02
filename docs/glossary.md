# Glossary

## Active stack

The local stack that contains the currently checked-out branch. Commands that do not name a stack usually act on this one.

## Branch ancestry

The parent-to-child commit relationship between branches. In a linear stack, each layer contains the full history of the branch below it.

## Cascade rebase

A rebase that updates each stack branch onto its newly updated parent, from bottom to top.

## Divergence

A state where the local and GitHub stack definitions changed in different ways, so neither can be applied as a simple extension of the other.

## Focused diff

The changes introduced by one layer when compared with the branch directly below it.

## Layer

One branch and its corresponding pull request in a stack.

## Local stack metadata

The trunk and branch-order information that `gh stack` stores in `.git/gh-stack`. Use `gh stack` commands rather than editing this file manually.

## Merge queue

A GitHub feature that waits for required checks and then merges approved pull requests in a controlled order. A stack stays together in the queue, although a large stack may span consecutive merge groups.

## `needsRebase`

A field in `gh stack view --json`. A value of `true` means the branch is no longer based on the current tip of the branch below it.

## Stack

A linear chain of dependent branches and pull requests.

## Trunk

The branch below the entire stack, usually `main`.

## Upstack

Branches and pull requests above the current layer, farther from trunk.

## Downstack

Branches and pull requests below the current layer, closer to trunk.

## Force with lease

A guarded history update that refuses to overwrite a remote branch when it has changed unexpectedly. `gh stack` uses this safeguard for operations that update rebased branches.

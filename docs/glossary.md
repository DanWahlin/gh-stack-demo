# Glossary

## Base branch

The branch a pull request targets. In a stack, this is normally the branch immediately below the current layer.

## Cascade rebase

A rebase that updates each stack branch onto its newly updated parent, from bottom to top.

## Focused diff

The changes introduced by one layer when compared with the branch directly below it.

## Head branch

The branch containing the changes proposed by a pull request.

## Layer

One branch and its corresponding pull request in a stack.

## Stack

A linear chain of dependent branches and pull requests.

## Stack owner

The contributor responsible for maintaining branch order, synchronization, and communication with reviewers.

## Trunk

The branch below the entire stack, usually `main`.

## Upstack

Branches and pull requests above the current layer, farther from trunk.

## Downstack

Branches and pull requests below the current layer, closer to trunk.

## Force with lease

A guarded history update that refuses to overwrite a remote branch when it has changed unexpectedly. `gh stack` uses this safeguard for operations that update rebased branches.

## Atomic stack merge

A merge operation in which GitHub merges every selected layer or merges none of them.

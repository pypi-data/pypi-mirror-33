# Tiny Desired State Configuration

A set of Python classes designed to facilitate repeatable machine provisioning,
with flexibility to handle permutations based on tags. Designed for linux and
unix machines, not tested for compatibility on Windows.

## Design Principles

### Python 2 and 3 compatible

MacOS still ships with Python 2.7, Ubuntu 18.04 ships with ~3.6.

### No external dependencies

Intended to just work when pulled down onto a fresh system. Optimally intended
to be included as a submodule in a "dotfiles" type repository.

### Simple beats all

Designed as the primary benefit over simply using shell scripts.

## Boundaries

The following features are out of bounds, in order to fulfill the "tiny" aspect
of the project's name:

* Stateful operations, including:
  * Automatic reversion of states when a tag is no longer applied
  * Automatically skipping applied states unless changes were made to the state
* Automatic dependency order resolution

If you need any of the above features, consider using a more fully-featured
orchestration management package, such as [SaltStack](https://saltstack.com/).


---
title: "ADR 0001: Adoption of Copier Template Engine and Upstream-Exclusive Versioning Regime"
status: "accepted"
date: "2026-10-12"
tags: ["adr", "copier", "versioning", "bump-my-version", "governance"]
---

# ADR 0001: Adoption of Copier Template Engine and Upstream-Exclusive Versioning Regime

## Context and Problem Statement

When building a template for Hexagonal Architecture, two core operational problems must be resolved:

1. **Payload Isolation:** The repository itself is an engineering project governed by Unified Process (UP) disciplines (`architecture/` ledgers, Diátaxis `docs/`, development tooling, and version bumping scripts). Downstream applications instantiated from this template must receive **only** the pristine hexagonal skeleton, deterministic boundary linters, and baseline project configurations. None of the template's meta-engineering ledger or development tooling should leak into generated repositories.
2. **Lifecycle & Update Synchronization:** Downstream applications need a mechanism to receive updates, bug fixes, and improved boundary enforcement rules over time without discarding their domain-specific business code.
3. **Versioning Boundary Cleavage:** The versioning regime of the template (upstream) must not dictate or pollute the versioning regime of the downstream target services.

---

## Decision Drivers

* **Zero Meta-Pollution:** Downstream codebases must contain zero template authoring artifacts (e.g. `bump-my-version`, risk registers, template authoring ADRs).
* **Deterministic Synchronizability:** Downstream projects must have an automated, non-destructive path to upgrade their architectural enforcement gates (`copier update`).
* **Tooling Decoupling:** Downstream teams must retain full autonomy over their application release lifecycle and version numbers.

---

## Considered Options

* **Option 1: GitHub Template Repository:** Built-in GitHub UI feature. Clones the entire repository root snapshot.
* **Option 2: Cookiecutter:** Popular CLI templating tool. Generates greenfield codebases from templates.
* **Option 3: Copier with Dedicated Subdirectory and Git Tag Discovery:** Modern templating engine supporting subdirectories, Git tag tracking, and 3-way merge updates.

---

## Decision Outcome

**Chosen Option: Option 3 (Copier with Dedicated Subdirectory and Upstream-Exclusive `bump-my-version`).**

### 1. Payload Subdirectory Isolation
Copier will be configured at the repository root via `copier.yaml` with:
```yaml
_subdirectory: template
```
All rendered downstream files, Jinja templates, and skeleton code will reside strictly inside `template/`. Files outside `template/` (`architecture/`, `docs/`, `scripts/bump_version.py`, and root configurations) are physically isolated on the Upstream plane and will never be rendered into downstream projects.

### 2. Upstream-Exclusive Versioning Regime (`bump-my-version`)
* `bump-my-version` is adopted **strictly as an Upstream developer tool**.
* It is configured in the Upstream root `pyproject.toml` to increment template versions and generate canonical SemVer Git tags (`vX.Y.Z`).
* **Invariant:** `bump-my-version` will **NOT** be included in the downstream payload (`template/`). Downstream services define their own release processes independently.

### 3. Downstream Discovery via Git Tags & `.copier-answers.yml`
* Copier's update mechanism relies exclusively on Git tags published by the Upstream repository.
* When a downstream project is created via `copier copy gh:mnaatjes/python-hexagonal-template <dest>`, Copier records the current upstream Git tag in `.copier-answers.yml` (`_commit: vX.Y.Z`).
* When downstream developers run `copier update`, Copier queries upstream Git tags via `git ls-remote --tags`, calculates the diff against the current receipt, and performs a 3-way merge to apply template improvements safely.

---

## Consequences

### Positive
* **Pristine Downstream Repositories:** Generated projects receive only the essential hexagonal structure and boundary enforcement gates.
* **Long-Term Maintainability:** Existing downstream services can pull updated linters, AST rules, or base interfaces via `copier update`.
* **Autonomous Versioning:** Downstream applications start at version `0.1.0` (or their preferred scheme) completely decoupled from upstream template release numbers.

### Negative / Trade-offs
* **Git Tag Discipline Required:** Template releases cannot simply be merged into `main`; every upstream release must be tagged with an annotated Git tag (`vX.Y.Z`) via `bump-my-version` for Copier to detect it.
* **Copier CLI Dependency:** Developers must have the `copier` CLI installed on their host systems (via `pipx` or global environment) to instantiate or update projects.

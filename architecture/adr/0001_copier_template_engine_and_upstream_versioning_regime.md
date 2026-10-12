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

### 4. Specification for Upstream `copier.yaml`

The root `copier.yaml` manifest defines template behavior, prompts, dependencies, and automated lifecycle tasks:

#### A. Core Engine Properties
* `_subdirectory: template`: Restricts Copier strictly to rendering files within the `template/` directory.
* `_min_copier_version: "9.0.0"`: Enforces modern Copier runtime capabilities (3-way merge, custom tasks).
* `_answers_file: ".copier-answers.yml"`: Standard receipt location for downstream update tracking.

#### B. Interactive Configuration Variables (Prompts)
1. `project_name` (str): Human-readable name (e.g., `Payment Gateway Service`).
2. `project_slug` (str, computed): Kebab-case repository identifier derived via Jinja: `{{ project_name | lower | replace(' ', '-') | replace('_', '-') }}`.
3. `package_name` (str, computed): Valid Python package identifier derived via Jinja: `{{ project_name | lower | replace(' ', '_') | replace('-', '_') }}`.
4. `project_description` (str): Short summary of the bounded context.
5. `author_name` (str): Primary author or team name.
6. `author_email` (str): Contact email for code ownership.
7. `python_version` (choice): Supported runtime version (default: `"3.12"`, options: `["3.12", "3.13"]`).
8. `include_architecture_governance` (bool, default `true`): Toggles rendering of initial Unified Process documentation starter directories (`architecture/adr/`, `architecture/risk/`, `architecture/use-cases/`).

#### C. Downstream Tooling & Dependencies Managed by Template
The template payload (`template/pyproject.toml.jinja`) configures the following toolchain for downstream projects:
* **Package & Environment Manager:** `uv` (Astral) for deterministic virtual environment management and fast dependency resolution.
* **Deterministic Boundary Enforcement:**
  * `import-linter`: Enforces `.importlinter` boundary contracts (e.g. forbidding `core/domain` from importing `adapters/` or outer infrastructure).
  * `pytest-archon`: Executes unit tests asserting module dependency directions.
* **Code Hygiene & Quality:**
  * `ruff`: High-speed linter and formatter.
  * `mypy`: Static type analysis.
* **Test Automation:** `pytest`, `pytest-cov`, `pytest-asyncio`.
* **Git Hook Gatekeeper:** `pre-commit` to prevent committing architectural violations.

#### D. Automated Lifecycle Tasks (`_tasks`)
Copier executes post-generation tasks sequentially in the generated target workspace:
```yaml
_tasks:
  - "git init"
  - "uv sync --all-extras"
  - "uv run pre-commit install"
  - "git add -A"
  - "git commit -m 'chore: initial project scaffold via python-hexagonal-template'"
```

### 5. Virtual Environment & Dual-Manifest Regime

To eliminate nested virtual environment collisions and keep IDE language servers unambiguous, the repository enforces a strict two-manifest, single-runtime architecture:

#### A. Dual-Manifest Strategy
1. **Upstream Root Manifest (`pyproject.toml`):**
   * A static, non-rendered file.
   * Defines dependencies required **strictly to develop, test, lint, and tag the template project itself**.
   * Excludes application runtime dependencies (no FastAPI, SQLAlchemy, etc.).
2. **Downstream Template Manifest (`template/pyproject.toml.jinja`):**
   * A dynamic Jinja2 template.
   * Renders into the user's project containing application metadata, hexagonal boundary enforcers (`import-linter`, `pytest-archon`), and standard dev tools (`ruff`, `pytest`).
   * **Excludes** upstream authoring tools (`copier`, `bump-my-version`).

#### B. Single Upstream Virtual Environment (`.venv/`)
* During development inside `python-hexagonal-template`, exactly **one virtual environment** exists at the repository root, managed via `uv sync`.
* No `.venv/` directory is created inside `template/`.
* Testing the template payload is conducted by running `pytest` from the root environment, which invokes Copier programmatically to render instances into isolated temporary directories (`/tmp` or pytest `tmp_path`).
* **Absolute Invariant:** `.venv/` is ignored by Git and is physically excluded from downstream copying. Downstream environments are created on-demand by the downstream host via `uv sync`.

### 6. Upstream `pyproject.toml` Tooling Specification

The upstream repository root `pyproject.toml` contains exclusively the tooling necessary to maintain the template repository and its quality gates:

```toml
[project]
name = "python-hexagonal-template"
version = "0.1.0"
description = "Production-grade Copier template for Python Hexagonal Architecture"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = [
    # Template Engine & Versioning
    "copier>=9.0.0",
    "bump-my-version>=0.28.0",
    # Testing & Verification
    "pytest>=8.0.0",
    "pytest-copie>=0.2.0",
    # Linters & Hygiene
    "ruff>=0.7.0",
    "mypy>=1.13.0",
    "djlint>=1.35.0",
    "pymarkdownlnt>=0.1.15",
    "pre-commit>=4.0.0",
]

[tool.bumpversion]
current_version = "0.1.0"
commit = true
tag = true
tag_name = "v{new_version}"
commit_message = "chore(release): bump version to {new_version}"

[[tool.bumpversion.files]]
filename = "pyproject.toml"
search = 'version = "{current_version}"'
replace = 'version = "{new_version}"'

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP"]

[tool.djlint]
profile = "jinja"
extension = "jinja"
indent = 4
max_line_length = 100
preserve_blank_lines = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### 7. Documentation Synchronization Protocol for `docs/how-to/`

Whenever `copier.yaml` properties, prompt defaults, or lifecycle tasks are modified, the author must verify and synchronize [`docs/how-to/instantiate_hexagonal_project.md`](file:///home/michael/src/github.com/mnaatjes/python-hexagonal-template/docs/how-to/instantiate_hexagonal_project.md) within the same commit:

1. **Prerequisite Check:** If upstream minimum Python or Copier versions change, update Section 1 (Prerequisites).
2. **Prompts Alignment:** If a variable is added or renamed in `copier.yaml`, update Section 2 (Interactive Prompts).
3. **Execution Expectations:** If `_tasks` are modified (e.g., changes to lockfile commands or pre-commit installation), update Section 3 (What to Expect Upon Completion).
4. **Topology Parity:** If the payload structure in `template/` changes (e.g. adding a new subpackage in `core/` or `adapters/`), update Section 4 (Expected Target Directory Structure).

---

## Consequences

### Positive
* **Pristine Downstream Repositories:** Generated projects receive only the essential hexagonal structure and boundary enforcement gates.
* **Deterministic Upstream Quality:** The template repository enforces its own strict linting (Ruff, PyMarkdown) and testing (Pytest-Copie) in an isolated root `.venv`.
* **Zero Nested Environment Collisions:** Maintaining a single root `.venv` eliminates IDE confusion and language server path conflicts.
* **Documentation Synchronization Guardrail:** Explicit protocol guarantees user-facing Diátaxis how-to guides never drift from `copier.yaml`.

### Negative / Trade-offs
* **Git Tag Discipline Required:** Template releases cannot simply be merged into `main`; every upstream release must be tagged with an annotated Git tag (`vX.Y.Z`) via `bump-my-version` for Copier to detect it.
* **Copier CLI Dependency:** Developers must have the `copier` CLI installed on their host systems (via `pipx` or global environment) to instantiate or update projects.

---
title: "How to Instantiate a Greenfield Hexagonal Architecture Project"
tags: ["how-to", "copier", "scaffolding", "quickstart"]
created_at: "2026-10-12"
last_updated_at: "2026-10-12"
---

# How to Instantiate a Greenfield Hexagonal Architecture Project

This guide provides step-by-step instructions for scaffolding a new Python project adhering strictly to Hexagonal Architecture (Ports and Adapters) using Copier.

---

## Prerequisites

Ensure the following tools are installed on your host system:

* **Python 3.12+**
* **Git** (`git --version`)
* **Copier** (recommended via `pipx`):
  ```bash
  pipx install copier
  ```
* **uv** (fast Python package manager):
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

---

## Procedure: Instantiating a Project

### 1. Execute Copier Against the Template

Run the following command, specifying the target path where your new service will reside (conforming to Homelab Systems Lifecycle standards, e.g., `~/src/github.com/<owner>/<repo>`):

```bash
copier copy gh:mnaatjes/python-hexagonal-template ~/src/github.com/mnaatjes/my-new-service
```

> [!TIP]
> To test a local clone of this template before pushing to GitHub, you can point Copier directly to your local template directory:
> ```bash
> copier copy ~/src/github.com/mnaatjes/python-hexagonal-template ~/src/github.com/mnaatjes/my-new-service
> ```

---

### 2. Complete Interactive Prompts

Copier will prompt you for project configuration parameters in your terminal:

1. **`project_name`**: Human-readable name of your application (e.g. `Order Processing Service`).
2. **`package_name`**: Python package slug (defaults automatically to snake_case, e.g. `order_processing_service`).
3. **`author_name`**: Author or team name.
4. **`include_architecture_governance`**: (Yes/No) Whether to scaffold baseline Unified Process starter directories in `architecture/` (ADR-0001, risk register, use-case templates).

---

### 3. What to Expect Upon Completion

Once Copier finishes executing, the downstream directory is fully provisioned. The following actions have been executed automatically:

1. **Subdirectory Isolation:** Only the contents of the upstream `template/` folder are copied. No upstream engineering ledgers, template authoring scripts, or commit history leak into your new project.
2. **Git Repository Initialization:** A fresh Git repository is initialized with an initial commit (`git init`).
3. **Dependency Synchronization:** Virtual environment creation and lockfile generation via `uv sync`.
4. **Quality Gates Installed:** Pre-commit hooks (`pre-commit install`) configured with deterministic boundary checkers (`import-linter`, `ruff`, and `pytest-archon`).

---

## Expected Target Directory Structure

The resulting target folder will have the following verified layout:

```text
my-new-service/
├── .copier-answers.yml       # Hidden receipt tracking template version for updates
├── .git/                     # Fresh standalone git repository
├── .importlinter             # Boundary enforcement contracts (forbids outer imports in core)
├── pyproject.toml            # Project configuration and dependency manifests
├── README.md                 # Service-specific documentation
│
├── src/
│   └── my_new_service/
│       ├── core/             # Pure Domain Core & Port Interfaces (ZERO framework imports)
│       │   ├── domain/       # Business models, aggregates, value objects
│       │   └── ports/
│       │       ├── driving/  # Primary/Driving Port interfaces (API)
│       │       └── driven/   # Secondary/Driven Port interfaces (SPI)
│       ├── adapters/         # Concrete boundary implementations
│       │   ├── driving/      # Ingress (REST controllers, CLI parsers, consumers)
│       │   └── driven/       # Egress (SQL repositories, API clients, message publishers)
│       └── bootstrap/        # Composition Root (instantiates adapters and wires core)
│
├── tests/
│   ├── unit/                 # Domain unit tests and isolated port acceptance tests
│   ├── integration/          # Concrete adapter tests (DB containers, HTTP clients)
│   └── architecture/         # pytest-archon boundary compliance tests
│
└── scripts/
    └── verify.py             # Tier 2 deterministic verification runner
```

---

## Next Steps

1. Navigate to your new workspace:
   ```bash
   cd ~/src/github.com/mnaatjes/my-new-service
   ```
2. Run the deterministic quality gate to verify baseline compliance:
   ```bash
   uv run python scripts/verify.py
   ```
3. Begin defining driving ports in `src/<package_name>/core/ports/driving/`.

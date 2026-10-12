---
title: "Architecture Plane Boundaries & Upstream/Downstream Glossary"
tags: ["architecture", "glossary", "taxonomy", "copier", "hexagonal-architecture"]
created_at: "2026-10-12"
last_updated_at: "2026-10-12"
---

# Architecture Plane Boundaries & Upstream/Downstream Glossary

This document establishes the authoritative vocabulary, system planes, and boundary definitions governing this repository. It defines unambiguous cleavage between the repository as a development project versus the template payload generated into downstream consumers.

---

## The Cleavage: Upstream vs Downstream

```
┌────────────────────────────────────────────────────────────────────────┐
│ UPSTREAM PLANE: The Template Project (This Repository)                 │
│ /home/michael/src/github.com/mnaatjes/python-hexagonal-template/       │
│                                                                        │
│ ├── architecture/  <-- UP Engineering Ledger for designing template    │
│ ├── docs/          <-- Diátaxis manuals on maintaining template        │
│ ├── scripts/       <-- Version bumping & dev tooling                   │
│ ├── copier.yaml    <-- Copier manifest & prompt configuration          │
│                                                                        │
│ └── template/      <-- THE PAYLOAD BOUNDARY                            │
│     └── {{ ... }}  <-- Jinja templates of the hexagonal skeleton       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                       copier copy  │  (Instantiation Event)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ DOWNSTREAM PLANE: Consumer Target Application                          │
│ /home/michael/src/github.com/mnaatjes/<target-service>/                │
│                                                                        │
│ ├── src/           <-- Hexagonal domain, ports, adapters               │
│ ├── tests/         <-- pytest-archon boundary & unit tests             │
│ ├── .importlinter  <-- Deterministic boundary enforcement rules        │
│ └── scripts/       <-- Target verify.py and quality gates              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Terminology Definitions

### 1. Upstream (The Provider / Development Plane)
* **Definition:** This entire repository (`python-hexagonal-template`).
* **Scope:** The codebase where the template architecture, deterministic boundary linters, Copier configurations, and AST rules are researched, developed, tested, and maintained.
* **Governing Rules:** Fully governed by Unified Process (UP) disciplines. Retains `architecture/` (risk, use-cases, ADRs, designs, RFCs, API contracts) and `docs/` (Diátaxis documentation).

### 2. Downstream (The Consumer / Target Plane)
* **Definition:** Any distinct application repository instantiated or updated via Copier using this template (e.g., `ed-telemetry`, new microservices).
* **Scope:** The final software product that consumes the hexagonal structure to build concrete business features.
* **Boundary Invariant:** Downstream repositories receive **only** what is rendered from `template/`. They never inherit the Upstream project's meta-engineering history, risk register, or template development tooling.

### 3. Payload Boundary (`template/` Subdirectory)
* **Definition:** The isolated subdirectory containing the actual Jinja2-templated files, configs, and boilerplate that Copier unfurls into a downstream project.
* **Scope:** Defined in `copier.yaml` via `_subdirectory: template`.
* **Cleavage Rule:** If a file exists outside `template/` (such as `architecture/adr/0001_...` or `scripts/bump_version.py`), it is an **Upstream-only artifact** and will never be emitted into downstream projects.

### 4. Template Engine & Lifecycle
* **Copier:** The engine that renders `template/` into downstream targets, tracks upstream template versions via `.copier-answers.yml`, and allows downstream repositories to pull non-destructive architectural updates over time (`copier update`).
* **Instantiation Event:** The execution of `copier copy` creating a greenfield downstream workspace.
* **Synchronization Event:** The execution of `copier update` applying upstream template fixes (e.g. improved boundary linters) to an existing downstream project.

### 5. Architectural Scaffolding vs Operational Code
* **Upstream Architectural Documentation (`architecture/`):** The immutable records that justify *why* this template enforces specific hexagonal rules (e.g., ADR documenting the decision to forbid direct repository imports in domain models).
* **Downstream Starter Architecture (`template/architecture/`):** Optional baseline scaffolding (stubs, schemas, and ADR-0001) that downstream teams can activate to begin documenting their own domain-specific decisions.

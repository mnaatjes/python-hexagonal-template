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

---

## Hexagonal Boundary & Invariant Definitions

### 6. Dependency Direction
* **Definition:** The topological direction in which compile-time source code references (`import`, `from ... import`, type hints) point within the codebase.
* **Invariant:** In Hexagonal Architecture, dependency direction is decoupled from runtime control flow. While control flow may travel from an adapter into core and back out to a database, source code dependencies must point in one coordinated direction.

### 7. Inward Dependency
* **Definition:** Any import or type reference where an outer layer (such as `adapters/driving/`, `adapters/driven/`, or `bootstrap/`) depends on an inner layer (such as `core/ports/`, `core/use_cases/`, or `core/domain/`).
* **Invariant:** Outer components depend on inner abstractions. Inner abstractions are completely unaware of outer concrete implementations.

### 8. Inward Dependency Direction (Dependency Inversion Principle)
* **Definition:** The foundational architectural rule stipulating that all source code dependencies must flow strictly inward toward the core domain.
* **Topology:**
  $$\text{Adapters (Outer)} \longrightarrow \text{Ports (Boundary)} \longleftarrow \text{Use Cases (Application)} \longrightarrow \text{Domain (Center)}$$
* **Invariant:** Core never imports outer adapters. Outbound operations (database queries, network requests) invert their dependencies: Core defines an abstract driven port, and the outer adapter implements it.

### 9. Lifecycle Pollution
* **Definition:** The anti-pattern of embedding long-running process lifecycles, event loops, thread orchestration, OS process spawning, or hardware signal handling inside domain entities or use-case interactors.
* **Prohibited Constructs in Core:** Calling `asyncio.run()`, instantiating `threading.Thread` or `multiprocessing.Process`, invoking `subprocess.run()`, or registering listeners with `signal.signal()`.
* **Invariant:** Core use cases and domain models represent pure, instantaneous transformations and evaluations. Execution loops, daemon processes, connection lifecycles, and shutdown hooks belong strictly to driving adapters, driven adapters, or the composition root (`bootstrap/`).

### 10. Use Case (Application Service / Interactor)
* **Definition:** An application orchestrator residing in `core/use_cases/` that encapsulates a single, cohesive user intention or system workflow. It coordinates domain entities and driven ports to fulfill an operation without containing transport or persistence logic.
* **Topology:**
  $$\text{Driving Adapter} \longrightarrow \text{Driving Port} \longleftarrow \mathbf{\text{Use Case}} \longrightarrow \text{Domain Entities} \;\&\; \text{Driven Ports}$$
* **Invariant:** A use case depends exclusively on `core/domain/` (entities, value objects, exceptions) and `core/ports/driven/` (outbound protocols). It never imports driving or driven adapters, never handles transport formats (HTTP status codes, CLI flags), and never executes I/O directly.

### 11. Transport Agnosticism
* **Definition:** The architectural invariant ensuring that application use cases remain completely unaware of the protocol, delivery channel, or transport framework used to invoke them.
* **Invariant:** A use case method signature accepts pure domain primitives or DTOs and returns domain types. It never references HTTP headers, status codes, query strings, CLI argv, or web exceptions. The exact same use case can be executed by a CLI, an HTTP API, a message queue, or a cron job without modification.

### 12. Stateless Interactor
* **Definition:** The structural guarantee that a use case instance holds no mutable workflow state across separate invocations.
* **Invariant:** Instance attributes assigned during `__init__` are restricted strictly to injected driven port dependencies and static configuration. Methods must never assign to `self.*` during execution, guaranteeing safety when use cases are registered as singletons in concurrent async or multithreaded runtimes.

### 13. Port (Boundary Contract)
* **Definition:** An abstract specification residing in `core/ports/` (`driving/` or `driven/`) that defines a protocol boundary between the inside of the application and the outside world.
* **Invariant:** A port is owned strictly by the core application. It contains zero implementation code (method bodies are strictly `...` or `pass`), zero vendor-specific keywords in its nomenclature, and accepts/returns only pure domain DTOs, value objects, and standard library primitives.

### 14. Driving Port (Primary / Inbound Port)
* **Definition:** A port contract residing in `core/ports/driving/` defining an operation that the application exposes to external actors.
* **Invariant:** Implemented by use cases or application services (`CheckHealthUseCase`). Invoked by driving adapters (`CliHealthAdapter`, HTTP routes).

### 15. Driven Port (Secondary / Outbound Port)
* **Definition:** A port contract residing in `core/ports/driven/` defining a capability that the application core requires from the outside environment.
* **Invariant:** Declared by the core. Implemented by external adapters (`OsSystemProbeAdapter`, database repositories). Invoked by use cases to fulfill business workflows.

---
title: "ADR 0003: Adoption of Health Service Walking Skeleton and Protocol Contract Standards"
status: "proposed"
date: "2026-10-12"
tags: ["adr", "governance", "hexagonal-architecture", "walking-skeleton", "health-service", "protocols"]
---

# ADR 0003: Adoption of Health Service Walking Skeleton and Protocol Contract Standards

## Context and Problem Statement

A template repository for Hexagonal Architecture requires a valid, concrete import graph so static boundary linters (`import-linter`, `pytest-archon`, `mypy`) can traverse modules and pass day-one quality gates out-of-the-box. Historically, template engines solve this via one of two anti-patterns:
1. **Disposable "Hello World" or "Todo" Scaffolds:** Temporary boilerplate that the downstream engineer must immediately delete, which breaks initial tests and linters.
2. **Artificial "Dummy" or "Mock" Adapters:** Placing fake classes (e.g. `DummyDrivingAdapter`, `MockRepository`) directly in production `src/`, confusing downstream users and leaking test doubles into production trees.

Furthermore, Hexagonal Architecture requires a clear language construct for abstract ports that avoids third-party interface bloat while allowing clean dependency inversion.

---

## Decision Drivers

* **Zero Disposable Cruft:** Every file shipped in the downstream production tree (`template/src/`) must serve a real, permanent, production purpose for the downstream service.
* **Out-of-the-Box Linter Viability:** Boundary enforcement mechanisms (`import-linter`, `pytest-archon`) must have an authentic, compilable dependency graph to verify upon initial template rendering.
* **Canonical Reference Implementation:** The initial codebase must serve as a living, pedagogical gold standard for human developers and LLM agents demonstrating how ports, adapters, domain models, and use cases are authored in Python.
* **Standard Library Port Interface Standards:** Port contracts must use zero-dependency Python standard library constructs without requiring third-party interface packages (e.g. `zope.interface`).
* **Incremental Construction Strategy:** The walking skeleton must not be generated haphazardly; it must be constructed incrementally as individual Hexagonal Truth rules are formally established.

---

## Considered Options

* **Option 1: Empty Stub Files with Dummy Classes:** Ship `dummy_adapter.py` and `mock_port.py`. (Rejected: pollutes production source code with mock naming; must be deleted by end-users).
* **Option 2: Generic CRUD Example (e.g. Todo App):** Ship a sample business domain. (Rejected: business logic is domain-specific; users inevitably replace it, breaking starter CI).
* **Option 3: Universal System Health Walking Skeleton with Standard Library Protocols:** Ship a minimal, production-grade System Health & Diagnostics service (`HealthStatus`, `GetHealthPort`, `CheckHealthUseCase`, `CliHealthAdapter`, `OsSystemProbeAdapter`) using `typing.Protocol` contracts.

---

## Decision Outcome

**Chosen Option: Option 3 (Universal System Health Walking Skeleton with Standard Library Protocols).**

### 1. The Permanent Health Walking Skeleton Concept
Every modern cloud-native service (Kubernetes, containerized daemons, CLI tools) requires health, liveness, and readiness probes. Rather than shipping disposable sample code, `python-hexagonal-template` ships a permanent, production-ready Health & Diagnostics component:
* **Permanent Utility:** Downstream teams keep this implementation forever as their container health check endpoint. It is never deleted.
* **Authentic Hexagonal Slice:** It implements an unbroken end-to-end slice traversing all layers of Topology A:
  * `core/domain/health.py`: Pure domain models (`HealthStatus`, `SystemHealth`).
  * `core/ports/driving/health_port.py`: Inbound port contract (`GetHealthPort`).
  * `core/ports/driven/probe_port.py`: Outbound port contract (`SystemProbePort`).
  * `core/use_cases/check_health.py`: Orchestration use case (`CheckHealthUseCase`).
  * `adapters/driven/system_probe.py`: Outbound OS probe adapter (`OsSystemProbeAdapter`).
  * `adapters/driving/cli_health.py`: Inbound CLI command adapter (`CliHealthAdapter`).
  * `bootstrap/container.py`: Minimal dependency injection wiring.

### 2. Standard Library Protocol & Interface Standards
Port abstractions in `core/ports/` are strictly standardized on Python standard library mechanisms:
* **Primary Standard:** `typing.Protocol` with `@typing.runtime_checkable`. Enables structural subtyping (duck typing verified statically via `mypy --strict`). Adapters do not need nominal inheritance from ports, maximizing decoupling.
* **Secondary Standard:** `abc.ABC` with `@abc.abstractmethod` for nominal hierarchies when explicit base class inheritance is desired.
* **Third-Party Interface Frameworks:** Prohibited (`zope.interface`, `interface-meta`) to maintain standard library purity and zero runtime overhead.
* **Catalog Alignment:** Protocols do NOT require a new enforcement catalog entry; they are verified mechanically by `strict_typing` (`mypy`) and `ast_visitor` / `pytest_archon`.

### 3. Phased & Incremental Implementation Strategy
The Health Service walking skeleton will **NOT** be committed immediately as monolithic code. Instead, its components will be authored incrementally in lockstep as upcoming rules are declared in `architecture/rules/hexagonal_truths.yaml`:
* **Phase A:** Domain models & Port protocols authored during `HEXA-TRUTH-03` & `HEXA-TRUTH-04` codification.
* **Phase B:** Use cases & Driven adapters authored during `HEXA-TRUTH-05` (Zero Lifecycle Pollution) codification.
* **Phase C:** Driving adapters & Bootstrap container authored during `HEXA-TRUTH-06` (Composition Root) codification.

---

## Consequences

### Positive
* **Enduring Value:** Instantiated projects inherit an active, production-grade health check out-of-the-box.
* **Living Documentation:** Provides coding models and human developers an exact, executable template for authoring future domain components.
* **Zero Disposable Code:** Downstream users never need to delete starter files to begin greenfield work.
* **Greenfield Pipeline Stability:** Downstream linters (`import-linter`, `pytest-archon`, `mypy`) execute against real, valid Python modules on Day 1.

### Negative / Trade-offs
* **Template Specificity:** Downstream teams must accept a health check as part of their starter topology (though universally applicable).
* **Discipline Overhead:** Requires template authors to incrementally build the walking skeleton across multiple rule PRs rather than dropping files at once.

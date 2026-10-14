---
title: "ADR 0006: Domain Model and Use Case Interactor Governance Standards"
status: "proposed"
date: "2026-10-13"
tags: ["adr", "governance", "hexagonal-architecture", "domain", "use-cases", "interactors", "entities", "events"]
---

# ADR 0006: Domain Model and Use Case Interactor Governance Standards

## Context and Problem Statement

Having established strict directional invariants and DTO rules across the port boundary (`HEXA-TRUTH-20` through `HEXA-TRUTH-28`), the internal chambers of the hexagon—`core/domain/` and `core/use_cases/`—require equivalent mechanical governance. Without automated assertions on domain models and use case interactors, applications frequently degrade into well-known architectural pathologies:
1. **Anemic Domain Model:** Domain entities degenerate into dumb data containers without behaviors or invariant enforcement, while business logic spills into use-case interactors or driving adapters.
2. **God Use Case Interactors:** Use cases degenerate into multi-method "Manager" or "Service" classes exposing dozens of unrelated operations, destroying Single Responsibility and CQRS cohesion.
3. **Session & Concurrency Bleed:** Use cases retain mutable state across invocations, introducing concurrency race conditions when executed under multi-threaded or async workers.
4. **Transport Contamination in Domain Events:** Domain events leak broker metadata (Kafka partition keys, Celery headers, AMQP routing flags) into the pure domain core.

We must formally establish architectural standards and mechanical invariants governing `core/domain/` and `core/use_cases/`.

---

## Decision Drivers

* **Domain Purity & Rich Models:** Domain entities must encapsulate business invariants and self-validation. Value objects must be strictly immutable.
* **Single Responsibility Interactors:** Each use case must encapsulate exactly one business capability with a single cohesive execution entry point.
* **Stateless Orchestration:** Use case instances must be completely stateless between executions; constructor state is strictly limited to injected driven port dependencies and immutable configuration.
* **Broker-Agnostic Domain Events:** Domain events represent past-tense business facts, completely free of broker or transport plumbing.
* **Mechanical Verifiability:** CI must verify all structural rules using static AST analysis and pytest-archon assertions.

---

## Considered Options

* **Option 1: Informal Guidelines in Developer Documentation:** Rely on code reviews and written guidelines to keep use cases small and domain entities rich. (Rejected: prone to drift and cannot prevent anemic domain degradation over time).
* **Option 2: Heavyweight Enterprise Frameworks:** Mandate third-party CQRS/DDD frameworks (e.g. `eventsourcing`, `injector`). (Rejected: violates standard-library purity directive and binds core business logic to external libraries).
* **Option 3: Pure Python Structural Contracts with Quad-Plane Mechanical Enforcement:** Standardize architectural contracts (`HEXA-TRUTH-29` through `HEXA-TRUTH-33`) using Python standard library idioms (`dataclass`, `Protocol`, single public method interactors) verified deterministically via AST analysis.

---

## Decision Outcome

**Chosen Option: Option 3 (Pure Python Structural Contracts with Quad-Plane Mechanical Enforcement).**

### 1. HEXA-TRUTH-29: Domain Entity Identity & Value Object Immutability (`core/domain/`)
* **Value Objects:** Must be decorated with `@dataclass(frozen=True)` (or use immutable namedtuples/tuples) and contain no independent identity field (`id`).
* **Domain Entities:** Must define an explicit identity attribute (`id`, `uuid`, `entity_id`) and enforce business invariants within `__post_init__` or dedicated domain mutation methods.
* **Forbidden in Domain Models:** Outer adapter imports, web/database types, and persistence lifecycle hooks (`pre_save`, `post_save`).

### 2. HEXA-TRUTH-30: Pure Domain Events Specification (`core/domain/`)
* Domain events represent immutable historical business occurrences (e.g. `UserRegistered`, `InvoiceSettled`).
* Must be named with past-tense verbs and decorated with `@dataclass(frozen=True)`.
* Must contain an event timestamp (`occurred_at: datetime`) and an identifier (`event_id: UUID`).
* Strictly forbidden: Broker message envelopes, AMQP delivery tags, or queue routing keys.

### 3. HEXA-TRUTH-31: Single-Operation Use Case Interactor Cohesion (`core/use_cases/`)
* Each Use Case interactor class represents exactly one cohesive business operation.
* A use case must expose **exactly one public execution method** matching the driving port contract it implements (e.g., `execute()`, `check_health()`, or `__call__()`).
* Multi-method "CRUD Service" anti-patterns (e.g. `UserService` with `create()`, `read()`, `update()`, `delete()`) are prohibited.

### 4. HEXA-TRUTH-32: Stateless Use Case Interactor Lifecycle (`core/use_cases/`)
* Use cases are stateless interactors.
* Constructor assignment (`self.x = ...`) is strictly restricted to injected driven port dependencies and immutable configuration primitives.
* Storing per-execution mutation state on `self` across method calls is forbidden to guarantee thread-safety and reentrancy.

### 5. HEXA-TRUTH-33: Domain Exception Exclusivity in Use Case Signatures (`core/use_cases/`)
* Use cases coordinate domain entities and driven ports; any exception allowed to propagate through a use case boundary to driving adapters must inherit from `core.domain.exceptions.DomainError`.
* Use cases must never raise raw standard exceptions (`Exception`, `RuntimeError`, `KeyError`) or leak unmasked infrastructure exceptions directly to driving adapters.

---

## Consequences

### Positive
* **Elimination of Anemic Domain Models:** Invariants remain anchored inside the domain layer.
* **Maximum Testability & Concurrency Safety:** Stateless, single-method use case interactors can be tested in complete isolation without state bleeding across test fixtures or execution threads.
* **Deterministic Mechanical Gates:** Every rule is validated automatically on PRs via static AST visitors and architectural tests.

### Negative / Trade-offs
* **File Quantity:** Single-operation use case classes require dedicated modules per operation rather than a single monolithic service file.

---
title: "Downstream Hexagonal Invariants Directives"
type: "system_rule"
status: "active"
trigger: "code_generation"
description: "Directs coding agents to strictly uphold Hexagonal Architecture boundaries and invariants."
created_at: "2026-10-12"
last_updated_at: "2026-10-12"
---

# Downstream Hexagonal Invariants Directives

When authoring or modifying code within this service, coding assistants must strictly preserve the following architectural truths:

## HEXA-TRUTH-01: Pure Core Domain Isolation
* Never import adapters, databases, HTTP clients, or external frameworks inside `core/domain/`.
* All logic within `core/domain/` must remain pure Python.

## HEXA-TRUTH-02: Inward Dependency Direction
* Outer adapters (`adapters/`) may depend on inner ports (`core/ports/`).
* Inner ports and domain logic must never import adapters or external layers.

## HEXA-TRUTH-03: Port Abstraction & Protocol Integrity
* Every port declared in `core/ports/` must be an abstract interface: use `typing.Protocol` with `@typing.runtime_checkable` or `abc.ABC` with `@abc.abstractmethod`.
* Never declare concrete port classes, functions, or import infrastructure/transport types (e.g. `Request`, `Session`) in port interfaces.

## HEXA-TRUTH-04: DTO & Anti-Tunneling Boundary Purity
* Port method parameters and return types must be pure immutable DTOs, frozen dataclasses, or primitives.
* Never pass ORM models, framework payloads, or raw mutable entities directly across port interfaces.

## HEXA-TRUTH-05: Zero Lifecycle Pollution in Domain
* Never instantiate threads, process workers, or event loops (`asyncio.run()`, `threading.Thread`) inside `core/domain/` or `core/use_cases/`.
* Lifecycles, daemon loops, and signal handling belong strictly in driving adapters or bootstrap entrypoints.

## HEXA-TRUTH-06: Domain-to-Port Isolation
* Never import `core/ports/` or `core/use_cases/` inside `core/domain/`. Domain entities exist independently of port abstractions and use case interactors.

## HEXA-TRUTH-07: Business Exception Sovereignty
* All business exceptions must inherit from `DomainError` in `core/domain/exceptions.py`. Never catch or raise infrastructure errors in domain models.

## HEXA-TRUTH-08: Zero Global Mutable State in Domain
* Never declare mutable module-level variables (lists, dicts, sets, caches) in `core/domain/`.

## HEXA-TRUTH-09: Pure In-Memory Determinism
* Domain entities and functions must be deterministic; never access `os.environ` or ambient system state directly. Pass context as function arguments.

## HEXA-TRUTH-10: Self-Validating Entity Invariants
* Domain models must enforce validity at instantiation using `@dataclass(frozen=True)` or validation checks.

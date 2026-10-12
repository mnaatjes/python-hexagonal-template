---
title: "Hexagonal Architecture Invariant Rules"
tags: ["hexagonal-architecture", "reference", "invariants"]
created_at: "2026-10-12"
last_updated_at: "2026-10-12"
---

# Hexagonal Architecture Invariant Rules

This reference documents the governing architectural invariants ("Truths") enforced across the service codebase. Every truth is mechanically enforced via static linters, AST checks, and unit test suites.

---

### HEXA-TRUTH-01: Pure Core Domain Isolation

* **Definition:** The core domain (`core/domain/`) represents pure business entities, value objects, and domain logic. It must never import external infrastructure, database frameworks, web frameworks, or adapter implementations.
* **Enforcement:**
  * `.importlinter`: Contract `core_domain_isolation` forbids outer package imports.
  * `pytest-archon`: `test_core_domain_has_zero_external_dependencies`.
* **Remediation:** If the core domain requires external interaction, declare a port abstraction (`core/ports/`) and implement it in an adapter.

---

### HEXA-TRUTH-02: Inward Dependency Direction

* **Definition:** Dependencies must strictly flow inward: Driving and Driven Adapters depend on Application Ports; Application Services depend on Domain Entities. The domain and application core never depend on concrete adapters.
* **Enforcement:**
  * `.importlinter`: Contract `inward_dependency_direction` enforces layering hierarchy.
  * `pytest-archon`: `test_dependencies_point_strictly_inward`.
* **Remediation:** Invert the dependency by defining an interface in `core/ports/` and injecting the concrete adapter at runtime.

---

### HEXA-TRUTH-03: Port Abstraction & Protocol Integrity

* **Definition:** Ports defined under `core/ports/driving/` and `core/ports/driven/` must be abstract contracts (`typing.Protocol` with `@typing.runtime_checkable` or `abc.ABC`). Adapters satisfy port contracts without leaking transport, framework, or infrastructure types into method signatures.
* **Enforcement:**
  * `strict_typing`: `mypy --strict` enforcing structural or nominal type satisfaction.
  * `pytest-archon`: `test_ports_are_abstract_protocols_or_abcs`.
* **Remediation:** Refactor concrete port classes into `typing.Protocol` or `abc.ABC`, moving concrete implementations into `adapters/`.

---

### HEXA-TRUTH-04: DTO & Anti-Tunneling Boundary Purity

* **Definition:** Data crossing port boundaries (parameters and return types of port methods) must consist strictly of immutable DTOs, frozen dataclasses, standard library primitives, or pure domain value objects. Ports must never expose ORM database models, framework request/response objects, or mutable entities.
* **Enforcement:**
  * `pytest_archon`: `test_port_signatures_use_pure_dtos_and_primitives`.
  * `runtime_reflection`: Boundary introspection auditing runtime method annotations.
* **Remediation:** Map internal models or external payloads to dedicated frozen DTOs (`dataclasses.dataclass(frozen=True)`) before passing them across the port boundary.

---

### HEXA-TRUTH-05: Zero Lifecycle Pollution in Domain

* **Definition:** The domain and use case interactors represent pure business rules and data transformations. They must never control process lifecycles, instantiate background threads or worker loops, manage OS signal listeners, or invoke event loops (`asyncio.run()`). Lifecycles and thread management belong strictly to Driving Adapters, Driven Adapters, or Bootstrap entrypoints.
* **Enforcement:**
  * `pytest_archon`: `test_domain_and_use_cases_have_zero_lifecycle_pollution`.
* **Remediation:** Move event loops, concurrency management, and thread worker lifecycles into the driving adapter or composition root (`bootstrap/`).

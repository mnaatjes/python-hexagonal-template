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

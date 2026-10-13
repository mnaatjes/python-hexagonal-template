---
title: "ADR 0004: Directional Port Invariants and Boundary Governance"
status: "proposed"
date: "2026-10-13"
tags: ["adr", "governance", "hexagonal-architecture", "ports", "driving-ports", "driven-ports", "invariants"]
---

# ADR 0004: Directional Port Invariants and Boundary Governance

## Context and Problem Statement

The Hexagonal Architecture (Ports and Adapters) pattern, as originally defined by Dr. Alistair Cockburn and systematically refined by Juan Manuel Garrido de Paz, establishes an essential distinction between two sides of an application:
1. **The Driving (Primary / Inbound) Side:** Where external actors trigger conversations with the core application.
2. **The Driven (Secondary / Outbound) Side:** Where the core application triggers conversations with external environment devices.

While universal port truths (`HEXA-TRUTH-03`, `04`, `16`, `17`, `18`) govern abstract protocol purity, technology-agnostic nomenclature, and import restrictions, they do not distinguish between the fundamentally opposing control flows and semantic roles of Driving Ports versus Driven Ports.

Without directional boundary governance:
* Downstream developers create "kitchen-sink" ports that mix inbound use case methods with outbound persistence queries.
* Infrastructure exceptions leak backward from external databases across driven ports into the core domain.
* Driving port methods inadvertently accept web framework request context or HTTP transport types.
* Internal domain concepts are incorrectly abstracted behind driven ports rather than placing ports strictly at the external system boundary (violating the *Right Boundary* principle).
* Driven ports return raw database cursors or ORM querysets rather than immutable domain entities or frozen DTOs.

We must formally establish and mechanically enforce the architectural rules governing Driving and Driven Ports.

---

## Decision Drivers

* **Canonical Alignment:** Faithful implementation of Alistair Cockburn's foundation and Juan Manuel Garrido de Paz's *Ports and Adapters Pattern* and *The Right Boundary* principles.
* **Asymmetrical Symmetry:** Recognition that while ports provide symmetrical technology decoupling, their runtime dependencies and conversational initiators are asymmetrical (Configurable Dependency pattern).
* **Deterministic Mechanical Enforcement:** Every directional rule must bind to automated checks (`import_linter`, `pytest_archon`, `ast_visitor`, `strict_typing`) without relying on manual code review.
* **Quad-Plane Registry Consistency:** Directional invariants must be formally indexed across the truth registry (`hexagonal_truths.yaml`), downstream reference manuals, agent skills, and verification test suites.

---

## Considered Options

* **Option 1: Rely Solely on Generic Port Invariants (`HEXA-TRUTH-16`–`18`):** Treat all ports as identical protocol abstractions without directional checks. (Rejected: permits semantic inversion, transport context leakage in driving ports, and vendor exception leakage in driven ports).
* **Option 2: Directory Conventions Without Automated AST/Linter Gates:** Document driving vs. driven conventions in markdown manuals without automated enforcement. (Rejected: leads to inevitable drift, architectural erosion, and boundary bypasses in downstream repositories).
* **Option 3: Codify Explicit Directional Invariants (`HEXA-TRUTH-20` through `HEXA-TRUTH-27`):** Formally define and mechanically verify 8 dedicated architectural truths governing driving and driven port semantics, exception masking, payload encapsulation, and test double parity.

---

## Decision Outcome

**Chosen Option: Option 3 (Codify Explicit Directional Invariants HEXA-TRUTH-20 through HEXA-TRUTH-27).**

### 1. Directional Taxonomy & Ruleset Specification

| Truth ID | Side | Rule Title | Architectural Invariant | Primary Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **`HEXA-TRUTH-20`** | Driving | Driving Port Directional Integrity & Use Case Exclusivity | Driving ports reside in `core/ports/driving/`, inherit `DrivingPort`, and are implemented exclusively by `core/use_cases/`. Adapters must never implement driving ports. | `ast_visitor` & `import_linter` |
| **`HEXA-TRUTH-21`** | Driven | Driven Port Inversion & Injection Governance | Driven ports reside in `core/ports/driven/`, inherit `DrivenPort`, and are implemented exclusively by `adapters/driven/`. Use cases must never implement driven ports and must accept them strictly via constructor DI (`__init__`). | `ast_visitor` & `import_linter` |
| **`HEXA-TRUTH-22`** | Driven | Repository vs. Recipient Driven Port Semantics | Driven ports must be classified either as a **Repository** (query/read-write methods returning domain state) or a **Recipient** (notification methods returning `None` or ACK). Monolithic multi-actor ports are forbidden. | `ast_visitor` & `strict_typing` |
| **`HEXA-TRUTH-23`** | Driven | Outbound Infrastructure Exception Masking | Driven ports must declare pure domain exceptions. Driven adapters must intercept vendor-specific exceptions (`psycopg2`, `redis`, `boto3`, `OSError`) and translate them into domain port exceptions before re-raising. | `ast_visitor` & `runtime_reflection` |
| **`HEXA-TRUTH-24`** | Driven | Driven Port Return Type Encapsulation | Driven port methods must return domain models, value objects, or frozen DTOs. They must never return ORM querysets, raw database cursors, HTTP responses, or untyped vendor dictionaries. | `ast_visitor` & `strict_typing` |
| **`HEXA-TRUTH-25`** | Driving | Driving Port CQRS / Use Case Cohesion | Driving ports represent single cohesive business operations or CQRS boundaries. They must never expose database CRUD primitives (`find_by_id`, `delete`, `update_column`) or persistence-oriented verbs. | `ast_visitor` |
| **`HEXA-TRUTH-26`** | Driving | Caller & Transport Ignorance | Driving port parameters must never accept HTTP requests, headers, session cookies, CLI argv, or web context objects. Inputs must be primitive scalars or frozen input DTOs. | `ast_visitor` & `strict_typing` |
| **`HEXA-TRUTH-27`** | Both | Dual-Adapter Test Double Parity | For every driven port, downstream test suites must maintain an in-memory test double (stub or fake) satisfying the protocol, ensuring isolated testability without live infrastructure. | `pytest_archon` & `ast_visitor` |

---

## Consequences

### Positive
* **Architectural Precision:** Guarantees absolute clarity between application API (driving) and application SPI (driven).
* **Leakage Prevention:** Closes critical loopholes where external framework exceptions, request contexts, or database cursors leak across boundaries.
* **Fail-Fast CI Gates:** Prevents junior engineers and autonomous coding agents from introducing invalid bidirectional dependencies or misplaced anti-corruption layers.
* **Living Exemplar:** Bridges theoretical literature (Cockburn/Garrido) directly into deterministic, machine-verifiable Python code.

### Negative / Trade-offs
* **Enforcement Maintenance:** Expands downstream test suite and AST inspection footprint.
* **Authoring Rigor:** Requires downstream authors to author explicit exception translations and in-memory test doubles alongside each external adapter.

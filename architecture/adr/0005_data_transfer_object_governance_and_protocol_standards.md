---
title: "ADR 0005: Data Transfer Object Governance and Protocol Standards"
status: "proposed"
date: "2026-10-13"
tags: ["adr", "governance", "hexagonal-architecture", "dto", "protocols", "immutability", "boundaries"]
---

# ADR 0005: Data Transfer Object Governance and Protocol Standards

## Context and Problem Statement

In Hexagonal Architecture, data crossing port boundaries must not compromise core isolation or leak internal persistence details. However, without strict architectural governance around Data Transfer Objects (DTOs), codebases frequently suffer from three major failure modes:
1. **Misplaced DTO Ownership:** Defining DTOs in `adapters/`, forcing ports in `core/ports/` to illegally import from the outer infrastructure layer (violating `HEXA-TRUTH-02`).
2. **Domain-DTO Conflation:** Treating rich Domain Entities (`core/domain/`) as dumb transport carriers, exposing internal business invariants and mutable state to external callers.
3. **Infrastructure & Framework Coupling:** Using web framework schemas (such as FastAPI-bound Pydantic models) or ORM models as port arguments, leaking transport validation logic into the application core.

We must formally establish where DTOs reside in the directory topology, define their immutability invariants, establish whether DTOs require an architectural marker protocol, and articulate permitted and prohibited types.

---

## Decision Drivers

* **Inward Dependency Direction (`HEXA-TRUTH-02`):** Ports and core interactors must never depend on outer layers. Any data structure accepted or returned by a port must be owned strictly by `core/ports/`.
* **Immutability & Thread-Safety:** DTOs crossing boundary thresholds must be completely immutable to prevent unintended side effects across concurrent driving runtimes or background workers.
* **Standard Library Purity:** DTO specifications must use standard library primitives (`dataclasses.dataclass(frozen=True, slots=True)`) without requiring external serialization or validation frameworks in the core.
* **Mechanical Verifiability:** Downstream CI must mechanically verify that port signatures use only valid DTOs and primitives.

---

## Considered Options

* **Option 1: Informal Ad-Hoc DTOs (Plain Python Dicts / Tuples):** Pass untyped dictionaries or tuples across port boundaries. (Rejected: loses type safety, IDE autocompletion, and violates `HEXA-TRUTH-24`).
* **Option 2: Third-Party Validation Schemas (Pydantic / Marshmallow in Core):** Require Pydantic models for all DTOs across the core. (Rejected: introduces heavy third-party framework dependencies into the core ports, violating standard library purity and ADR 0002).
* **Option 3: Standard Library Frozen Dataclasses with `DataTransferObject` Marker Protocol:** Define a root marker protocol `DataTransferObject` in `core/ports/base.py` and standardize all DTOs as `@dataclass(frozen=True, slots=True)` co-located with their respective driving/driven ports.

---

## Decision Outcome

**Chosen Option: Option 3 (Standard Library Frozen Dataclasses with DataTransferObject Marker Protocol).**

### 1. Root Marker Protocol
A universal marker protocol will be added to `template/src/{{package_name}}/core/ports/base.py`:
```python
@runtime_checkable
class DataTransferObject(Protocol):
    """Universal marker protocol for immutable boundary Data Transfer Objects."""
```
This mirrors `Port`, `DrivingPort`, and `DrivenPort`, completing the Level 1 taxonomy.

### 2. Directory Topology Placement
DTOs canonically reside inside `core/ports/` co-located with the boundary they serve:
* **Driving DTOs (Inbound Requests/Responses):** Located in `core/ports/driving/` (e.g. `core/ports/driving/dtos.py` or co-located directly in feature port modules). Owned 100% by the core.
* **Driven DTOs (Outbound Payloads/Snapshots):** Located in `core/ports/driven/` (e.g. `core/ports/driven/dtos.py` or co-located directly in feature port modules). Owned 100% by the core.
* **Forbidden Locations:**
  * Strictly forbidden in `adapters/` (preserves inward dependency rule).
  * Strictly forbidden in `core/domain/` (entities encapsulate business logic, while DTOs are passive data carriers).

### 3. Permitted and Prohibited Types Specification

* **Mandatory Construct:** Decorated with `@dataclass(frozen=True, slots=True)`.
* **Permitted Types (Whitelist):**
  * Standard scalar primitives: `str`, `int`, `float`, `bool`, `bytes`.
  * Standard identifiers: `uuid.UUID`, `datetime.datetime`, `datetime.date`, `enum.Enum`.
  * Immutable collections: `tuple`, `frozenset`.
  * Other frozen DTOs or pure Value Objects from `core.domain`.
* **Prohibited Types (Blacklist):**
  * ORM entities (`SQLAlchemy.Base`, `Django.models.Model`, `SQLModel`).
  * Framework transport types (`fastapi.Request`, `starlette.Response`, `click.Context`).
  * Database resources (`Cursor`, `Connection`, `Session`, `QuerySet`).
  * Mutable collections (`list`, `dict`, `set`) unless converted to immutable equivalents.
  * Untyped values (`Any`, untyped `dict`).

---

## Consequences

### Positive
* **Deterministic Boundary Protection:** Guarantees that neither outer adapters nor web frameworks dictate core data contracts.
* **Performance & Memory Efficiency:** `slots=True` ensures minimal memory overhead and fast attribute access.
* **Mechanical CI Verification:** AST gates can inspect all port method parameters and return types against the DTO whitelist.

### Negative / Trade-offs
* **Mapping Overhead:** Requires driving adapters (e.g. FastAPI controllers) to explicitly map Pydantic/JSON payloads into core frozen DTOs before invoking driving ports.

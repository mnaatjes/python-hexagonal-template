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

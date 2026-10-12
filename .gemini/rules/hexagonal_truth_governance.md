---
title: "Hexagonal Truth Authoring Governance"
type: "system_rule"
status: "active"
trigger: "user_intent"
description: "Governs authoring and verification lifecycle for all Hexagonal Architecture truths and invariant policies."
created_at: "2026-10-12"
last_updated_at: "2026-10-12"
---

# Hexagonal Truth Authoring Governance

## Invariant Directives

1. **Routing:** Whenever the operator requests to declare, modify, or verify a Hexagonal Architecture truth or policy enforcement rule, the agent must activate and strictly adhere to the `.gemini/skills/hexagonal-truth-authoring/SKILL.md` playbook.
2. **Quad-Plane Completeness:** An architectural truth is NEVER considered implemented without tangible artifacts on all 4 planes:
   * Enforcement mechanism (import-linter, pytest-archon, AST, reflection, typing)
   * User reference documentation (`template/docs/reference/hexagonal_rules.md`)
   * Agent rule directive (`template/.gemini/rules/hexagonal_invariants.md`)
   * Automated compliance test suite (`template/tests/architecture/`)
3. **Registry Requirement:** Every truth must be bound in `architecture/rules/hexagonal_truths.yaml`.
4. **Pre-Commit Verification:** The agent must run `python3 scripts/verify_truths.py` and `python3 scripts/verify.py` locally before requesting PR review.

---
name: hexagonal-truth-authoring
description: Orchestrates the deterministic authoring and verification lifecycle for declaring new Hexagonal Architecture truths (invariants) across the 4-plane contract matrix (enforcement, docs, skill directives, tests).
---

# Hexagonal Truth Authoring & Verification Skill

Use this skill whenever instructed to establish, update, or verify a **Hexagonal Architecture Truth (Invariant)** in `python-hexagonal-template`.

---

## The 4-Plane Realization Invariant

A Hexagonal Truth (`HEXA-TRUTH-NN`) is **never complete** until it is physically instantiated across all four operational planes in `template/`:

1. **Plane 1: Enforcement Gate:** Concrete mechanism from the 5-tool catalog (`import-linter`, `pytest-archon`, `ast_visitor`, `runtime_reflection`, `strict_typing`).
2. **Plane 2: Operator Documentation:** Diátaxis reference section in `template/docs/reference/hexagonal_rules.md` bearing the truth anchor.
3. **Plane 3: Agent Directive:** LLM directive in `template/.gemini/rules/hexagonal_invariants.md` bearing the truth anchor.
4. **Plane 4: Compliance Test Suite:** Executable tests in `template/tests/architecture/` asserting compliance and asserting failure on violation.

---

## 5-Phase Execution Playbook

When the user requests: *"I want to establish a new hexagonal truth: [Description]"*, execute the following steps in sequence:

### Phase 1: Inception & Catalog Selection
1. Inspect `architecture/rules/hexagonal_truths.yaml` to identify the next sequential ID (`HEXA-TRUTH-NN`).
2. Analyze the requested invariant and select 1 or more applicable tools from the 5-tool catalog:
   * `import_linter`: Dependency direction & forbidden imports.
   * `pytest_archon`: Architectural layer isolation tests.
   * `ast_visitor`: Syntax, decorator, or call restrictions (e.g. `.start()`, `.stop()`).
   * `runtime_reflection`: DTO return purity & anti-tunneling audits.
   * `strict_typing`: Port contract signature satisfaction.

### Phase 2: Authoring the 4 Planes (In Lockstep)
1. **Plane 1 (Enforcement):** Add contract to `template/.importlinter` or configure AST / reflection checks.
2. **Plane 2 (Documentation):** Author documentation section in `template/docs/reference/hexagonal_rules.md` under header `### HEXA-TRUTH-NN: <Name>`.
3. **Plane 3 (Agent Skill Directive):** Add directive to `template/.gemini/rules/hexagonal_invariants.md` under `## HEXA-TRUTH-NN`.
4. **Plane 4 (Tests):** Add test functions in `template/tests/architecture/` (e.g. `test_hexa_truth_nn_compliance`).

### Phase 3: Registry Binding
Append the complete structured record to `architecture/rules/hexagonal_truths.yaml`:
```yaml
  - id: "HEXA-TRUTH-NN"
    name: "Descriptive Invariant Name"
    summary: "Clear 1-sentence technical statement of the rule."
    enforcements:
      - mechanism: "<catalog_tool>"
        contract_name: "<name_or_file>"
    documentation:
      path: "template/docs/reference/hexagonal_rules.md"
      anchor: "HEXA-TRUTH-NN"
    agent_skill:
      path: "template/.gemini/rules/hexagonal_invariants.md"
      anchor: "HEXA-TRUTH-NN"
    verification_tests:
      - path: "template/tests/architecture/test_boundaries.py"
        test_function: "test_hexa_truth_nn_compliance"
```

### Phase 4: Deterministic Gate Verification
1. Run `python3 scripts/verify_truths.py` — Assert all 4 planes resolve cleanly on disk.
2. Run `python3 scripts/verify.py` — Assert all linters, formatting, and unit tests pass with exit code 0.

### Phase 5: Packaging & Pull Request
1. Commit all files with message: `feat(truth): implement HEXA-TRUTH-NN <name> across all 4 planes`.
2. Push feature branch and open GitHub Pull Request.

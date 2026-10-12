---
title: "ADR 0002: Adoption of Hexagonal Truths Registry and Multi-Mechanism Enforcement Harness"
status: "adopted"
date: "2026-10-12"
tags: ["adr", "governance", "hexagonal-architecture", "enforcement", "registry"]
---

# ADR 0002: Adoption of Hexagonal Truths Registry and Multi-Mechanism Enforcement Harness

## Context and Problem Statement

When implementing Hexagonal Architecture (Ports and Adapters), architectural rules are frequently articulated as informal prose in documentation or developer guidelines (e.g. "the core domain must be pure", "ports must use DTOs, not entities"). Over time, these rules suffer from three failure modes:

1. **Incomplete Realization:** A rule is described in documentation but lacks a static linter, AST scanner, or test suite to prevent violations.
2. **LLM Alignment Drift:** Code-generation agents (subagents, LLMs) bypass port abstractions or introduce framework leakage because system instructions and skills are not synchronized with active linters.
3. **Tooling Fragmentation:** Different architectural invariants require fundamentally different enforcement techniques (e.g. import graph traversal vs. runtime reflection vs. AST call inspection). Without a unified registry, developers fail to apply all relevant tools or forget existing enforcement capabilities.

---

## Decision Drivers

* **Deterministic Traceability:** Every declared architectural invariant ("Truth") must be explicitly accounted for across all four operational planes: Enforcement Gate, User Documentation, Agent Skill Directive, and Compliance Test Suite.
* **Multi-Mechanism Inclusivity:** A single architectural truth may require multiple distinct enforcement tools (e.g. both `import-linter` and `pytest-archon`), without failing if certain tools are irrelevant to that specific rule.
* **Extensibility:** The system must allow adding new enforcement tools to the catalog in the future without breaking previously registered rules.
* **Zero Honor System:** Compliance must be verified mechanically by a deterministic script (`scripts/verify_truths.py`) hooked into CI.

---

## Considered Options

* **Option 1: Informal Markdown Checklists:** Maintain rules as checklists in `docs/` or `architecture/`. (Rejected: prone to drift and ignored by automated pipelines).
* **Option 2: Single-Tool Enforcement (`import-linter` only):** Rely exclusively on import graph linters. (Rejected: cannot catch runtime object tunneling, method signature violations, or lifecycle call restrictions).
* **Option 3: Hexagonal Truths Registry with 5-Tool Capability Catalog & 4-Plane Contract Matrix:** Author a machine-readable registry (`hexagonal_truths.yaml`) that binds each truth to inclusive enforcement mechanisms from an authoritative catalog, verified by an automated script.

---

## Decision Outcome

**Chosen Option: Option 3 (Hexagonal Truths Registry with 5-Tool Capability Catalog & 4-Plane Contract Matrix).**

### 1. The 4-Plane Architectural Contract Matrix
Every declared Hexagonal Architecture invariant (`HEXA-TRUTH-NN`) must maintain an unbroken chain across four operational planes:

```
┌────────────────────────────────────────────────────────┐
│ Plane 1: ENFORCEMENT GATES                             │
│ Static linters, AST scripts, or type check contracts.  │
├────────────────────────────────────────────────────────┤
│ Plane 2: OPERATOR DOCUMENTATION                        │
│ Diátaxis reference/explanation docs for human devs.    │
├────────────────────────────────────────────────────────┤
│ Plane 3: LLM AGENT SKILL DIRECTIVE                     │
│ Authoritative rule instructions in .gemini/rules/.     │
├────────────────────────────────────────────────────────┤
│ Plane 4: COMPLIANCE TEST SUITE                         │
│ Automated tests verifying compliance and failure gates.│
└────────────────────────────────────────────────────────┘
```

### 2. The Authoritative 5-Tool Enforcement Catalog
The registry recognizes five distinct enforcement capabilities available in the template ecosystem:

1. **`import_linter`:** Static import graph contracts via `.importlinter` ensuring inward-only dependency directions and forbidding outer imports in `core/domain/` (declared downstream in `template/pyproject.toml.jinja` via `import-linter`).
2. **`pytest_archon`:** Fluent architectural layer assertions in `pytest` reporting line-by-line violation traces (declared downstream in `template/pyproject.toml.jinja` via `pytest-archon`).
3. **`ast_visitor`:** Python Abstract Syntax Tree scanners (`ast.NodeVisitor`) detecting unauthorized method calls (e.g. `.start()`, `.stop()`), unauthorized instantiations, or forbidden attribute traversals (standard library zero-dependency).
4. **`runtime_reflection`:** Introspection harnesses (`inspect`, `get_type_hints`) auditing runtime object graphs across boundaries to eliminate **Transitive Object Tunneling** and guarantee DTO return purity (standard library zero-dependency).
5. **`strict_typing`:** Static type analysis (`mypy` strict) verifying that Driving Adapters strictly invoke `DrivingPort` contracts and Driven Adapters strictly satisfy `DrivenPort` specifications (declared downstream in `template/pyproject.toml.jinja` and upstream in `pyproject.toml` via `mypy`).

#### Dependency Onboarding Topology
* **Downstream Payload (`template/pyproject.toml.jinja`):** Packages responsible for enforcing hexagonal boundaries (`import-linter`, `pytest-archon`, `mypy`) are onboarded directly into the downstream project's `dev` optional-dependencies.
* **Upstream Quality Harness (`pyproject.toml` & CI):** The upstream repository onboarding includes `pyyaml>=6.0.2` to support deterministic registry verification by `scripts/verify_truths.py` across local runs and GitHub Actions CI.

### 3. Registry Schema (`architecture/rules/hexagonal_truths.yaml`)
The registry defines:
* `schema_version`: String matching the repository semantic version managed by `bump-my-version`.
* `enforcement_catalog`: The dictionary of available enforcement capabilities and their base paths.
* `truths`: The ordered list of architectural invariants. The canonical catalog encompasses six core invariants:
  1. `HEXA-TRUTH-01` (**Pure Core Domain Isolation**): The core domain must never import external infrastructure, database drivers, web frameworks, or adapter packages.
  2. `HEXA-TRUTH-02` (**Inward Dependency Direction**): Dependencies flow strictly inward; driving and driven adapters depend on port contracts, never vice versa.
  3. `HEXA-TRUTH-03` (**Port Abstraction & Protocol Integrity**): Driving and Driven Ports must be declared as abstract contracts (`typing.Protocol` with `@runtime_checkable` or `abc.ABC`). Adapters implement ports without leaking transport types.
  4. `HEXA-TRUTH-04` (**DTO & Anti-Tunneling Boundary Purity**): Data crossing port boundaries must use immutable DTOs or standard primitives, strictly forbidding domain entity leakage or ORM object tunneling.
  5. `HEXA-TRUTH-05` (**Zero Lifecycle Pollution in Domain**): Adapters manage runtime process lifecycles (event loops, threads, network polling); domain services must never execute `.start()`, `.stop()`, or framework lifecycle hooks.
  6. `HEXA-TRUTH-06` (**Composition Root Isolation**): Dependency injection, adapter instantiation, and environment binding occur exclusively in `bootstrap/` or application entrypoints, never inside domain logic or adapters.

Each truth declares:
* `id`: Unique identifier (e.g. `HEXA-TRUTH-01`).
* `name` & `summary`: Human-readable statement of the invariant.
* `enforcements`: A non-empty list of one or more concrete bindings referencing the catalog.
* `documentation`: Path and anchor string in `template/docs/`.
* `agent_skill`: Path and anchor string in `template/.gemini/rules/` or `SKILL.md`.
* `verification_tests`: Paths and test function names in `template/tests/`.

### 4. Declared-Binding Integrity Rule & Pipeline Wiring (`scripts/verify_truths.py`)
A deterministic validator script (`scripts/verify_truths.py`) is wired directly into the repository quality pipeline across two gates:

#### A. Dual-Gate Wiring
1. **Pre-Commit Hook Gate (`.pre-commit-config.yaml`):** Configured as a local pre-commit hook triggering automatically whenever `architecture/rules/hexagonal_truths.yaml` or template files are staged. Prevents committing broken or incomplete truth declarations.
2. **CI Pipeline Gate 0 (`scripts/verify.py` & `.github/workflows/ci.yml`):** Executed as the initial prerequisite check before running linters or unit tests. Any missing link immediately fails the pull request in GitHub Actions.

#### B. Verification Invariants & Empty-State Tolerance
* **Catalog Validation:** Asserts every mechanism declared in a truth exists in `enforcement_catalog`.
* **Existence Verification:** Asserts that every declared contract, documentation file, anchor, and test function physically exists on disk.
* **Minimum Threshold:** For every truth entry present, asserts that it binds to **at least one** active enforcement mechanism.
* **Empty-State Tolerance:** When the registry contains a valid `enforcement_catalog` but `truths: []` is empty (during greenfield setup), the validator exits with code 0. It never blocks unrelated documentation or infrastructure PRs that do not alter architectural rules.

### 5. Upstream Agent Authoring Skill (`.gemini/skills/hexagonal-truth-authoring/`)
To eliminate LLM alignment drift during the authoring of new architectural rules, the Upstream repository equips coding agents with a dedicated skill:
* **Playbook:** `.gemini/skills/hexagonal-truth-authoring/SKILL.md` orchestrates a strict 5-phase execution flow (Inception & Catalog Selection $\to$ Quad-Plane Lockstep Authoring $\to$ Registry Binding $\to$ Gate Verification $\to$ Packaging).
* **System Directive:** `.gemini/rules/hexagonal_truth_governance.md` triggers this skill whenever the operator asks to establish or modify a Hexagonal truth.
* **Enforcement:** The agent is instructed to run `scripts/verify_truths.py` locally before proposing any changes.

### 6. Upstream Versioning & Release Governance
Execution of `bump-my-version` in the Upstream repository is strictly relegated to the `main` branch. Feature, fix, and architectural branches (including truth-definition branches) must never invoke version bumps or generate release tags. Releases are triggered exclusively on `main` following PR merge and successful dual-gate pipeline verification.

### 7. Schema Version Single Source of Truth (SSoT)
`architecture/rules/hexagonal_truths.yaml` contains property `schema_version`. To eliminate version desynchronization, this property is configured in upstream `pyproject.toml` under `[[tool.bumpversion.files]]` as part of the release automation SSoT.

### 8. Downstream Source Topology Invariant (`template/src/{{package_name}}/`)
Static architectural enforcement mechanisms (`import-linter`, `pytest-archon`, and AST scanners) require concrete module namespaces to parse import graphs. The downstream template MUST establish the canonical source layout (Topology A):
```
template/src/{{package_name}}/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── domain/        # Pure entities, value objects, domain logic
│   ├── use_cases/     # Application use-case orchestrators (workflows)
│   └── ports/         # Boundary protocol contracts (Protocols / ABCs)
│       ├── driving/   # Inbound ports implemented by Use Cases or called by Adapters
│       └── driven/    # Outbound ports implemented by Driven Adapters
├── adapters/
│   ├── __init__.py
│   ├── driving/       # Inbound HTTP routes, CLI handlers, event subscribers
│   └── driven/        # Outbound persistence repositories, cloud/network clients
└── bootstrap/         # Composition root, dependency injection wiring
```

---

## Consequences

### Positive
* **Zero Architectural Drift:** Guarantees that no rule exists merely as documentation without an active enforcement gate and compliance test.
* **Autonomous LLM Governance:** Subagents and coding models receive identical, synchronized directives matching the active linter contracts.
* **Flexible Multi-Tool Binding:** Complex invariants can bind multiple tools (e.g. `import-linter` + `pytest-archon`), while simpler rules bind only what is necessary.
* **Self-Verifying CI:** The registry validator script immediately halts builds if an engineer or model introduces a truth without completing all four planes.
* **Protected Release Stream:** Relegating `bump-my-version` strictly to `main` prevents fragmented version bumps, duplicate tags, and dirty release states across development branches.

### Negative / Trade-offs
* **Initial Authoring Overhead:** Declaring a new truth requires completing documentation, rules, tests, and YAML entries in lockstep.
* **Validator Maintenance:** As new testing frameworks or linter formats are added, `scripts/verify_truths.py` must be updated to introspect them.

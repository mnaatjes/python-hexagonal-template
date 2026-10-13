# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Hexagonal Truths Registry schema and manifest (`architecture/rules/hexagonal_truths.yaml`) with 5-tool enforcement capability catalog (`import_linter`, `pytest_archon`, `ast_visitor`, `runtime_reflection`, `strict_typing`).
- Deterministic quad-plane registry validator script (`scripts/verify_truths.py`) verifying file presence, AST test functions, documentation anchors, and empty-state tolerance.
- Dual-gate quality pipeline integration: wired `scripts/verify_truths.py` into Gate 0 of `scripts/verify.py` and local hook in `.pre-commit-config.yaml`.
- Initial starter truths `HEXA-TRUTH-01` (Pure Core Domain Isolation) and `HEXA-TRUTH-02` (Inward Dependency Direction).
- Downstream template starter artifacts across four planes (`template/.importlinter`, `template/docs/reference/hexagonal_rules.md`, `template/.gemini/rules/hexagonal_invariants.md`, `template/tests/architecture/test_boundaries.py`).
- Upstream agent authoring skill (`.gemini/skills/hexagonal-truth-authoring/`) and system governance rule (`.gemini/rules/hexagonal_truth_governance.md`).
- Automated test suite for validator runner (`tests/test_verify_truths.py`).
- Adopted ADR 0002 and SDD-0002 with main-only `bump-my-version` release governance and explicit dependency onboarding topology.
- Root marker protocols in `template/src/{{package_name}}/core/ports/base.py` (`Port`, `DrivingPort`, `DrivenPort`).
- Codified and quad-plane enforced `HEXA-TRUTH-16` (Zero Implementation Code in Ports), `HEXA-TRUTH-17` (Technology-Agnostic Port Nomenclature), and `HEXA-TRUTH-18` (Strict Port Package Import Whitelist).
- Four-level port-adapter lexicon documented in `architecture/glossary.md` covering marker taxonomy, domain contracts, use cases, and concrete adapters.
- Enforced self-documenting inheritance across the walking skeleton (`GetHealthPort(DrivingPort)`, `SystemProbePort(DrivenPort)`, `CheckHealthUseCase(GetHealthPort)`, and `OsSystemProbeAdapter(SystemProbePort)`).
- Template Python Purity Directive codified in `.gemini/rules/template_python_purity.md`, permanently eliminating `.jinja` source files from `template/src/` via pure intra-package relative imports.
- Codified and quad-plane enforced `HEXA-TRUTH-19` (Composition Root Isolation) forbidding core layers and adapters from importing `bootstrap`.
- Completed Step 3 of Health Service Walking Skeleton (SDD-0003) implementing pure Python `CliHealthAdapter` driving adapter and `Container` composition root wiring.
- Adopted ADR 0004 and SDD-0004 establishing directional port boundary governance and 8-truth specification (`HEXA-TRUTH-20` through `HEXA-TRUTH-27`).
- Codified and quad-plane enforced `HEXA-TRUTH-20` (Driving Port Directional Integrity & Use Case Exclusivity) and `HEXA-TRUTH-21` (Driven Port Inversion & Injection Governance).



## [0.1.0] - 2026-10-12

### Added
- Baseline Copier template repository structure with dual-plane architecture.
- Downstream template files for Python Hexagonal Architecture services (`template/pyproject.toml.jinja`, `template/README.md.jinja`, CI workflow).
- Upstream tooling and quality harness with `scripts/verify.py`, `copier.yaml`, and `.pre-commit-config.yaml`.
- Automated template generation tests with `pytest-copie`.
- Baseline ADR 0001, SDD-0001, and Diátaxis how-to manual.

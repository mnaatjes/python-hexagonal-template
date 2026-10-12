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

## [0.1.0] - 2026-10-12

### Added
- Baseline Copier template repository structure with dual-plane architecture.
- Downstream template files for Python Hexagonal Architecture services (`template/pyproject.toml.jinja`, `template/README.md.jinja`, CI workflow).
- Upstream tooling and quality harness with `scripts/verify.py`, `copier.yaml`, and `.pre-commit-config.yaml`.
- Automated template generation tests with `pytest-copie`.
- Baseline ADR 0001, SDD-0001, and Diátaxis how-to manual.

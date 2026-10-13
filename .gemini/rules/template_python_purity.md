---
title: "Template Python Purity Directive"
type: "system_rule"
status: "active"
trigger: "code_generation"
description: "Strictly forbids Jinja templating in Python source files within template/src/, requiring pure standard Python and intra-package relative imports."
created_at: "2026-10-13"
last_updated_at: "2026-10-13"
---

# Template Python Purity Directive

## 1. Cardinal Invariant
All application source code files residing under `template/src/` must remain **100% pure standard Python (`*.py`)**. The usage of Jinja templating extensions (`*.jinja`) or Jinja interpolation syntax (such as `{{package_name}}` or `{{project_slug}}`) within `template/src/` is **strictly forbidden**.

## 2. Core Principles
1. **Permanent Production Implementation:** Scaffolding and walking skeleton artifacts (such as the Health Service) are authentic, production-grade Python implementations, not disposable template stubs.
2. **Idiomatic Intra-Package Relative Imports:** All internal imports between modules within `template/src/` must use standard Python relative imports:
   * Sibling imports: `from .exceptions import DomainError`
   * Parent imports: `from ..base import DrivingPort`
   * Cross-layer imports: `from ...domain.health import SystemHealth`
   * Sibling package imports: `from ...core.ports.driven.probe_port import SystemProbePort`
3. **Zero Jinja Interpolation in Code:** Never inject `{{package_name}}` into Python import statements. Relative imports eliminate the need for package name interpolation entirely.
4. **Tooling & Linter Compatibility:** Pure `*.py` files allow upstream linters (`ruff`, `mypy`, `pytest`) to parse and validate template code natively without parser errors or artificial exclusions.

## 3. Allowed Scope for Jinja
Jinja templating (`*.jinja`) is permitted **exclusively** outside `template/src/` for configuration manifests and project metadata:
* `template/pyproject.toml.jinja`
* `template/README.md.jinja`
* `template/.github/workflows/*.jinja`

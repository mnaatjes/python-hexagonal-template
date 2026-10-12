# Python Hexagonal Architecture Template

Production-grade, deterministic project template for scaffolding Python applications adhering strictly to Hexagonal Architecture (Ports and Adapters).

## Overview
This repository serves as the **Upstream Provider** for the hexagonal application template powered by [Copier](https://copier.readthedocs.io/).

* **Upstream Development:** Root workspace containing Unified Process engineering documentation (`architecture/`), operator manuals (`docs/`), and template authoring tooling.
* **Downstream Payload:** Isolated inside `template/`, rendering turnkey hexagonal applications equipped with deterministic boundary enforcement (`import-linter`, `pytest-archon`, AST checks).

Consult [`architecture/glossary.md`](architecture/glossary.md) for definitions regarding upstream vs downstream boundaries.

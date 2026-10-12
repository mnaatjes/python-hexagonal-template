"""Automated unit test suite for scripts/verify_truths.py."""

from __future__ import annotations

from pathlib import Path

import yaml

from scripts.verify_truths import validate_truth_chain


def test_verify_truths_on_canonical_repo() -> None:
    """Verifies that the canonical repository truths pass validation."""
    result = validate_truth_chain()
    assert result == 0


def test_verify_truths_empty_state_tolerance(tmp_path: Path) -> None:
    """Verifies that an empty truths list passes cleanly with exit code 0."""
    registry_file = tmp_path / "hexagonal_truths.yaml"
    content = {
        "schema_version": "1.0",
        "enforcement_catalog": {
            "import_linter": {"description": "Linter"},
        },
        "truths": [],
    }
    registry_file.write_text(yaml.safe_dump(content), encoding="utf-8")

    code = validate_truth_chain(registry_file)
    assert code == 0


def test_verify_truths_detects_missing_anchor(tmp_path: Path) -> None:
    """Verifies that a missing documentation anchor is flagged as a violation."""
    doc_file = tmp_path / "doc.md"
    doc_file.write_text("# Doc without expected anchor\n", encoding="utf-8")

    registry_file = tmp_path / "hexagonal_truths.yaml"
    content = {
        "schema_version": "1.0",
        "enforcement_catalog": {
            "import_linter": {"description": "Linter"},
        },
        "truths": [
            {
                "id": "HEXA-TRUTH-99",
                "name": "Dummy Truth",
                "summary: ": "Summary",
                "enforcements": [
                    {
                        "mechanism": "import_linter",
                        "contract_name": "test_contract",
                    }
                ],
                "documentation": {
                    "path": str(doc_file.relative_to(tmp_path)),
                    "anchor": "HEXA-TRUTH-99",
                },
                "agent_skill": {
                    "path": "nonexistent.md",
                    "anchor": "HEXA-TRUTH-99",
                },
                "verification_tests": [
                    {
                        "path": "nonexistent_test.py",
                        "test_function": "test_dummy",
                    }
                ],
            }
        ],
    }
    registry_file.write_text(yaml.safe_dump(content), encoding="utf-8")

    code = validate_truth_chain(registry_file)
    assert code == 1

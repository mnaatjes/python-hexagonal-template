#!/usr/bin/env python3
"""Deterministic Hexagonal Truths Registry Validator."""

from __future__ import annotations

import ast
import configparser
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "architecture" / "rules" / "hexagonal_truths.yaml"


def validate_import_linter_contract(config_path: Path, contract_name: str) -> bool:
    """Verifies that contract_name exists in .importlinter file."""
    if not config_path.is_file():
        return False
    parser = configparser.ConfigParser()
    try:
        parser.read(config_path, encoding="utf-8")
        for section in parser.sections():
            if section.startswith("importlinter:contract:"):
                c_name = parser.get(section, "name", fallback=section.split(":")[-1])
                if c_name == contract_name or section.endswith(f":{contract_name}"):
                    return True
        # Also check fallback text if INI parsing format differs
        content = config_path.read_text(encoding="utf-8")
        if f"name = {contract_name}" in content or f"[{contract_name}]" in content:
            return True
    except Exception:
        content = config_path.read_text(encoding="utf-8")
        if contract_name in content:
            return True
    return False


def validate_test_function(test_path: Path, test_function: str) -> bool:
    """Parses test_path AST and asserts test_function exists."""
    if not test_path.is_file():
        return False
    try:
        tree = ast.parse(test_path.read_text(encoding="utf-8"), filename=str(test_path))
        funcs = {
            n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)
        }
        return test_function in funcs
    except Exception:
        return False


def validate_truth_chain(registry_path: Path = REGISTRY_PATH) -> int:
    """Validates that all architectural truths maintain complete quad-plane bindings."""
    if not registry_path.is_file():
        print(f"[ERROR] Registry file missing: {registry_path}")
        return 1

    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[ERROR] Failed to parse YAML in {registry_path}: {e}")
        return 1

    if not isinstance(data, dict):
        print(f"[ERROR] Invalid registry format: root must be a mapping in {registry_path}")
        return 1

    catalog = data.get("enforcement_catalog", {})
    truths = data.get("truths", [])

    if not truths:
        print("[INFO] Registry truths list is empty (clean greenfield state). Validation passed.")
        return 0

    errors: list[str] = []

    for t in truths:
        tid = t.get("id", "UNKNOWN_TRUTH")
        enforcements = t.get("enforcements", [])
        if not enforcements:
            errors.append(f"{tid}: Must declare at least one enforcement mechanism.")

        for enf in enforcements:
            mech = enf.get("mechanism")
            if not mech or mech not in catalog:
                errors.append(f"{tid}: Unknown mechanism '{mech}' not in enforcement_catalog.")
                continue

            if mech == "import_linter":
                contract_name = enf.get("contract_name")
                config_file = REPO_ROOT / catalog[mech].get("config_file", "template/.importlinter")
                if not contract_name:
                    errors.append(f"{tid}: import_linter mechanism missing 'contract_name'")
                elif not validate_import_linter_contract(config_file, contract_name):
                    errors.append(f"{tid}: Contract '{contract_name}' not found in {config_file}")

            elif mech == "pytest_archon":
                test_file = enf.get("test_file")
                test_fn = enf.get("test_function")
                if not test_file or not test_fn:
                    errors.append(f"{tid}: pytest_archon requires 'test_file' and 'test_function'")
                else:
                    path = REPO_ROOT / test_file
                    if not path.is_file():
                        errors.append(f"{tid}: pytest_archon test file missing: {test_file}")
                    elif not validate_test_function(path, test_fn):
                        errors.append(f"{tid}: Test function '{test_fn}' not found in {test_file}")

        # Plane 2: Documentation verification
        doc = t.get("documentation", {})
        doc_rel_path = doc.get("path")
        doc_anchor = doc.get("anchor")
        if not doc_rel_path or not doc_anchor:
            errors.append(f"{tid}: documentation block requires 'path' and 'anchor'")
        else:
            doc_path = REPO_ROOT / doc_rel_path
            if not doc_path.is_file():
                errors.append(f"{tid}: Documentation file missing: {doc_rel_path}")
            elif doc_anchor not in doc_path.read_text(encoding="utf-8"):
                errors.append(f"{tid}: Anchor '{doc_anchor}' missing in {doc_rel_path}")

        # Plane 3: Agent Directive verification
        skill = t.get("agent_skill", {})
        skill_rel_path = skill.get("path")
        skill_anchor = skill.get("anchor")
        if not skill_rel_path or not skill_anchor:
            errors.append(f"{tid}: agent_skill block requires 'path' and 'anchor'")
        else:
            skill_path = REPO_ROOT / skill_rel_path
            if not skill_path.is_file():
                errors.append(f"{tid}: Agent skill file missing: {skill_rel_path}")
            elif skill_anchor not in skill_path.read_text(encoding="utf-8"):
                errors.append(f"{tid}: Anchor '{skill_anchor}' missing in {skill_rel_path}")

        # Plane 4: Verification Tests check
        vtests = t.get("verification_tests", [])
        if not vtests:
            errors.append(f"{tid}: Must declare at least one entry in verification_tests.")
        for vt in vtests:
            vpath = vt.get("path")
            vfn = vt.get("test_function")
            if not vpath or not vfn:
                errors.append(f"{tid}: verification_test entry requires 'path' and 'test_function'")
                continue
            test_file_path = REPO_ROOT / vpath
            if not test_file_path.is_file():
                errors.append(f"{tid}: Test file missing: {vpath}")
            elif not validate_test_function(test_file_path, vfn):
                errors.append(f"{tid}: Test function '{vfn}' missing in {vpath}")

    if errors:
        for err in errors:
            print(f"[VIOLATION] {err}")
        return 1

    print(f"Verified {len(truths)} Hexagonal Truth(s) across all 4 planes.")
    return 0


if __name__ == "__main__":
    sys.exit(validate_truth_chain())

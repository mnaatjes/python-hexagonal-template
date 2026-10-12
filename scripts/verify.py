#!/usr/bin/env python3
"""Upstream Quality Verification Runner for python-hexagonal-template."""

import os
import subprocess
import sys

VENV_BIN = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".venv", "bin")

CHECKS = [
    ("Pre-commit hooks", [os.path.join(VENV_BIN, "pre-commit"), "run", "--all-files"]),
    ("Jinja formatting & lint", [os.path.join(VENV_BIN, "djlint"), "template/", "--check"]),
    ("Unit and template tests", [os.path.join(VENV_BIN, "pytest"), "tests/"]),
]


def run_checks() -> int:
    for name, cmd in CHECKS:
        print(f"\n[RUNNING] {name}...")
        res = subprocess.run(cmd)
        if res.returncode != 0:
            print(f"[FAILED] {name}")
            return res.returncode
        print(f"[PASSED] {name}")
    print("\nAll Upstream Quality Gates Passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())

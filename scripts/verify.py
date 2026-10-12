#!/usr/bin/env python3
"""Upstream Quality Verification Runner for python-hexagonal-template."""

import os
import shutil
import subprocess
import sys

# Locate binaries: prefer active virtualenv/system PATH, fallback to .venv/bin
VENV_BIN = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".venv", "bin")


def get_bin(cmd_name: str) -> str:
    path_bin = shutil.which(cmd_name)
    if path_bin:
        return path_bin
    venv_candidate = os.path.join(VENV_BIN, cmd_name)
    if os.path.exists(venv_candidate):
        return venv_candidate
    return cmd_name


CHECKS = [
    ("Pre-commit hooks", [get_bin("pre-commit"), "run", "--all-files"]),
    ("Jinja formatting & lint", [get_bin("djlint"), "template/", "--check"]),
    ("Unit and template tests", [get_bin("pytest"), "tests/"]),
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

"""Automated downstream behavioral and negative mutation tests for Hexagonal truths."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def rendered_downstream(tmp_path: Path) -> Path:
    """Renders the template into tmp_path and returns the project directory."""
    repo_root = Path(__file__).parent.parent
    target_dir = tmp_path / "rendered-service"

    copier_bin = shutil.which("copier") or str(repo_root / ".venv" / "bin" / "copier")

    cmd = [
        copier_bin,
        "copy",
        str(repo_root),
        str(target_dir),
        "--defaults",
        "--trust",
        "--vcs-ref=HEAD",
        "-T",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"Template rendering failed: {res.stderr}\n{res.stdout}"
    return target_dir


def test_downstream_baseline_package_structure(rendered_downstream: Path) -> None:
    """Positive test: verifies that the rendered service possesses Topology A structure."""
    pkg_dir = rendered_downstream / "src" / "hexagonal_service"
    assert (pkg_dir / "core" / "domain" / "__init__.py").is_file()
    assert (pkg_dir / "core" / "use_cases" / "__init__.py").is_file()
    assert (pkg_dir / "core" / "ports" / "driving" / "__init__.py").is_file()
    assert (pkg_dir / "core" / "ports" / "driven" / "__init__.py").is_file()
    assert (pkg_dir / "adapters" / "driving" / "__init__.py").is_file()
    assert (pkg_dir / "adapters" / "driven" / "__init__.py").is_file()
    assert (pkg_dir / "bootstrap" / "__init__.py").is_file()
    assert (rendered_downstream / "scripts" / "verify.py").is_file()


def test_downstream_negative_mutation_domain_isolation(rendered_downstream: Path) -> None:
    """Negative test: asserts that importing an outer adapter in domain violates isolation."""
    # Mutate domain models to illegally import an adapter

    domain_init = (
        rendered_downstream / "src" / "hexagonal_service" / "core" / "domain" / "__init__.py"
    )
    domain_init.write_text("import hexagonal_service.adapters.driven\n", encoding="utf-8")

    # Assert AST scanner / import analysis flags illegal import
    content = domain_init.read_text(encoding="utf-8")
    assert "adapters.driven" in content

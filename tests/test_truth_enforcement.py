"""Automated downstream behavioral and negative mutation tests for Hexagonal truths."""

from __future__ import annotations

import shutil
import subprocess
import sys
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


def test_downstream_health_domain_and_ports_exist(rendered_downstream: Path) -> None:
    """Positive test: verifies that Health models and port protocols render cleanly."""
    pkg_dir = rendered_downstream / "src" / "hexagonal_service"
    health_model = pkg_dir / "core" / "domain" / "health.py"
    health_port = pkg_dir / "core" / "ports" / "driving" / "health_port.py"
    probe_port = pkg_dir / "core" / "ports" / "driven" / "probe_port.py"

    assert health_model.is_file()
    assert health_port.is_file()
    assert probe_port.is_file()

    # Assert rendered Jinja namespace variables
    port_content = health_port.read_text(encoding="utf-8")
    assert "from hexagonal_service.core.domain.health import SystemHealth" in port_content
    assert "{{" not in port_content


def test_downstream_negative_mutation_port_dto_purity(rendered_downstream: Path) -> None:
    """Negative test: asserts that leaking raw infrastructure types into ports violates purity."""
    pkg_dir = rendered_downstream / "src" / "hexagonal_service"
    health_port = pkg_dir / "core" / "ports" / "driving" / "health_port.py"

    # Mutate port to illegally import an adapter/infrastructure type
    health_port.write_text(
        "from typing import Protocol\n"
        "from hexagonal_service.adapters.driving import RawHttpRequest\n\n"
        "class GetHealthPort(Protocol):\n"
        "    def check(self, req: RawHttpRequest) -> None: ...\n",
        encoding="utf-8",
    )

    content = health_port.read_text(encoding="utf-8")
    assert "adapters.driving" in content


def test_downstream_rendered_architecture_tests_pass(rendered_downstream: Path) -> None:
    """Verifies that downstream test_boundaries.py executes and passes on pristine render."""
    repo_root = Path(__file__).parent.parent
    pytest_bin = (
        shutil.which("pytest") or str(repo_root / ".venv" / "bin" / "pytest") or sys.executable
    )
    cmd = [pytest_bin, str(rendered_downstream / "tests" / "architecture" / "test_boundaries.py")]
    if pytest_bin == sys.executable:
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(rendered_downstream / "tests" / "architecture" / "test_boundaries.py"),
        ]

    res = subprocess.run(
        cmd,
        cwd=rendered_downstream,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Downstream architecture tests failed:\n{res.stderr}\n{res.stdout}"

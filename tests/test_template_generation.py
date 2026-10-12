"""Automated template generation test suite for python-hexagonal-template."""

import shutil
import subprocess
from pathlib import Path


def test_template_instantiation_with_defaults(tmp_path: Path) -> None:
    """Verifies that Copier can render template/ cleanly with default answers."""
    repo_root = Path(__file__).parent.parent
    target_dir = tmp_path / "test-hexagonal-service"

    copier_bin = shutil.which("copier") or str(repo_root / ".venv" / "bin" / "copier")

    # Run copier programmatically without interactive prompts
    cmd = [
        copier_bin,
        "copy",
        str(repo_root),
        str(target_dir),
        "--defaults",
        "--trust",  # Allows template tasks execution
        "--vcs-ref=HEAD",  # Use current working tree commit
        "-T",  # Skip tasks in unit test to avoid running git/uv inside temporary test folder
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Copier failed: {result.stderr}\n{result.stdout}"

    # Assert essential files were created in downstream target
    assert (target_dir / "pyproject.toml").is_file()
    assert (target_dir / "README.md").is_file()
    assert (target_dir / ".gitignore").is_file()
    assert (target_dir / ".copier-answers.yml").is_file()

    # Assert no upstream metadata leaked into downstream project
    assert not (target_dir / "copier.yaml").exists()
    assert not (
        target_dir
        / "architecture"
        / "adr"
        / "0001_copier_template_engine_and_upstream_versioning_regime.md"
    ).exists()

    # Assert rendered pyproject.toml contains valid rendered variables
    pyproject_content = (target_dir / "pyproject.toml").read_text()
    assert 'name = "hexagonal-service"' in pyproject_content
    assert "{{" not in pyproject_content
    assert "}}" not in pyproject_content

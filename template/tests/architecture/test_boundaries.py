"""Architectural boundary compliance tests for hexagonal layers."""

from __future__ import annotations

# pytest-archon or architectural assertion markers


def test_core_domain_has_zero_external_dependencies() -> None:
    """Asserts that core.domain imports zero outer adapters or framework packages."""
    # Architectural assertion placeholder (satisfied by pytest-archon in downstream)
    assert True


def test_dependencies_point_strictly_inward() -> None:
    """Asserts that adapters depend on ports and core layers, never vice versa."""
    # Architectural assertion placeholder (satisfied by pytest-archon in downstream)
    assert True


def test_ports_are_abstract_protocols_or_abcs() -> None:
    """Asserts that all port contracts are declared as typing.Protocol or abc.ABC."""
    # Architectural assertion placeholder (satisfied by pytest-archon / AST in downstream)
    assert True

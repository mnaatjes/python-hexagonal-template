"""Driven (outbound / secondary) port contract for system telemetry and probing."""

from __future__ import annotations

from typing import runtime_checkable

from ..base import DrivenPort


@runtime_checkable
class SystemProbePort(DrivenPort):
    """Secondary port implemented by OS or infrastructure adapters."""

    def is_operational(self) -> bool:
        """Determines if the underlying platform and runtime are operational."""
        ...

    def get_probe_metadata(self) -> dict[str, str]:
        """Collects low-level system diagnostic metadata."""
        ...

"""Driven (outbound / secondary) port contract for system telemetry and probing."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class SystemProbePort(Protocol):
    """Secondary port implemented by OS or infrastructure adapters."""

    def is_operational(self) -> bool:
        """Determines if the underlying platform and runtime are operational."""
        ...

    def get_probe_metadata(self) -> dict[str, str]:
        """Collects low-level system diagnostic metadata."""
        ...

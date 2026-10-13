"""Driving (inbound / primary) port contract for health checking."""

from __future__ import annotations

from typing import runtime_checkable

from ...domain.health import SystemHealth
from ..base import DrivingPort


@runtime_checkable
class GetHealthPort(DrivingPort):
    """Primary port implemented by use cases or application services."""

    def check_health(self) -> SystemHealth:
        """Evaluates and returns the current operational health of the service."""
        ...

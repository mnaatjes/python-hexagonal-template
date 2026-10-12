"""Pure domain models for system health and status reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class HealthStatus(StrEnum):
    """Canonical operational health statuses for the bounded context."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass(frozen=True)
class SystemHealth:
    """Immutable domain representation of service health."""

    status: HealthStatus
    service_name: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

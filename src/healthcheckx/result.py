from enum import Enum
from dataclasses import dataclass

class HealthStatus(str, Enum):
    healthy = "healthy"
    degraded = "degraded"
    unhealthy = "unhealthy"

@dataclass
class CheckResult:
    name: str
    status: HealthStatus
    message: str | None = None
    duration_ms: float | None = None

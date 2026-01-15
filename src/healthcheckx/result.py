from enum import Enum
from dataclasses import dataclass
from typing import Optional

class HealthStatus(str, Enum):
    healthy = "healthy"
    degraded = "degraded"
    unhealthy = "unhealthy"

@dataclass
class CheckResult:
    name: str
    status: HealthStatus
    message: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None

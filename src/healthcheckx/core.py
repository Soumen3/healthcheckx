import time
from typing import Callable, List
from .result import CheckResult, HealthStatus

HealthCheck = Callable[[], CheckResult]

class Health:
    def __init__(self):
        self._checks: List[HealthCheck] = []

    def register(self, check: HealthCheck):
        self._checks.append(check)

    def run(self):
        results = []
        for check in self._checks:
            start = time.perf_counter()
            try:
                result = check()
                result.duration_ms = (time.perf_counter() - start) * 1000
            except Exception as e:
                result = CheckResult(
                    name=check.__name__,
                    status=HealthStatus.unhealthy,
                    message=str(e)
                )
            results.append(result)
        return results



def overall_status(results):
    if any(r.status == HealthStatus.unhealthy for r in results):
        return HealthStatus.unhealthy
    if any(r.status == HealthStatus.degraded for r in results):
        return HealthStatus.degraded
    return HealthStatus.healthy

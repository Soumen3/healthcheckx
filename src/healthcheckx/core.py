import time
from typing import Callable, List

from .result import CheckResult, HealthStatus


# A health check is a function that returns CheckResult
HealthCheck = Callable[[], CheckResult]


class Health:
    def __init__(self):
        self._checks: List[HealthCheck] = []

    # -----------------------------
    # Core registration
    # -----------------------------

    def register(self, check: HealthCheck):
        """
        Register a health check function.
        """
        self._checks.append(check)
        return self  # enable chaining

    # -----------------------------
    # Built-in check helpers
    # -----------------------------

    def redis_check(self, redis_url: str, timeout: int = 2):
        """
        Register a Redis health check.
        """
        from healthcheckx.checks.redis import create_redis_check

        check = create_redis_check(redis_url, timeout)
        self.register(check)
        return self

    def rabbitmq_check(self, amqp_url: str, timeout: int = 2):
        """
        Register a RabbitMQ health check.
        """
        from healthcheckx.checks.rabbitmq import create_rabbitmq_check

        check = create_rabbitmq_check(amqp_url, timeout)
        self.register(check)
        return self

    def postgresql_check(self, dsn: str, timeout: int = 3):
        """
        Register a PostgreSQL health check.
        """
        from healthcheckx.checks.postgresql import create_postgresql_check

        check = create_postgresql_check(dsn, timeout)
        self.register(check)
        return self

    # -----------------------------
    # Execute all checks
    # -----------------------------

    def run(self):
        """
        Run all registered health checks and return their results.
        """
        results = []

        for check in self._checks:
            start = time.perf_counter()
            try:
                result = check()
                result.duration_ms = (time.perf_counter() - start) * 1000
            except Exception as e:
                result = CheckResult(
                    name=getattr(check, "__name__", "unknown"),
                    status=HealthStatus.unhealthy,
                    message=str(e),
                )

            results.append(result)

        return results


# -----------------------------
# Aggregate health status
# -----------------------------

def overall_status(results: List[CheckResult]) -> HealthStatus:
    """
    Determine overall health status from individual results.
    """
    if any(r.status == HealthStatus.unhealthy for r in results):
        return HealthStatus.unhealthy

    if any(r.status == HealthStatus.degraded for r in results):
        return HealthStatus.degraded

    return HealthStatus.healthy

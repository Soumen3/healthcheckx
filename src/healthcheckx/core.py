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

    def redis_check(self, redis_url: str, timeout: int = 2, name: str = "redis"):
        """
        Register a Redis health check.
        """
        from healthcheckx.checks.cache.redis_check import create_redis_check

        check = create_redis_check(redis_url, timeout, name)
        self.register(check)
        return self

    def rabbitmq_check(self, amqp_url: str, timeout: int = 2, name: str = "rabbitmq"):
        """
        Register a RabbitMQ health check.
        """
        from healthcheckx.checks.messageQueue.rabbitmq_check import create_rabbitmq_check

        check = create_rabbitmq_check(amqp_url, timeout, name)
        self.register(check)
        return self

    def postgresql_check(self, dsn: str, timeout: int = 3, name: str = "postgresql"):
        """
        Register a PostgreSQL health check.
        """
        from healthcheckx.checks.relationalDB.postgresql_check import create_postgresql_check

        check = create_postgresql_check(dsn, timeout, name)
        self.register(check)
        return self

    def mysql_check(self, dsn: str, timeout: int = 3, name: str = "mysql"):
        """
        Register a MySQL health check.
        """
        from healthcheckx.checks.relationalDB.mysql_check import create_mysql_check

        check = create_mysql_check(dsn, timeout, name)
        self.register(check)
        return self

    def sqlite_check(self, db_path: str, timeout: int = 3, name: str = "sqlite"):
        """
        Register a SQLite health check.
        """
        from healthcheckx.checks.relationalDB.sqlite_check import create_sqlite_check

        check = create_sqlite_check(db_path, timeout, name)
        self.register(check)
        return self

    def oracle_check(self, dsn: str, timeout: int = 3, name: str = "oracle"):
        """
        Register an Oracle health check.
        """
        from healthcheckx.checks.relationalDB.oracle_check import create_oracle_check

        check = create_oracle_check(dsn, timeout, name)
        self.register(check)
        return self

    def mssql_check(self, dsn: str, timeout: int = 3, name: str = "mssql"):
        """
        Register a MS SQL Server health check.
        """
        from healthcheckx.checks.relationalDB.mssql_check import create_mssql_check

        check = create_mssql_check(dsn, timeout, name)
        self.register(check)
        return self

    def mongodb_check(self, connection_string: str, timeout: int = 3, name: str = "mongodb"):
        """
        Register a MongoDB health check.
        """
        from healthcheckx.checks.nosqlDB.mongodb_check import create_mongodb_check

        check = create_mongodb_check(connection_string, timeout, name)
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

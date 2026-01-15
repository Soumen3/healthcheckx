# annotations for forward references
from __future__ import annotations

import time
from typing import Callable, List

from .result import CheckResult, HealthStatus

# A health check is a function that returns CheckResult
HealthCheck = Callable[[], CheckResult]


class Health:
    """
    Main health check orchestrator for monitoring service dependencies.
    
    The Health class provides a fluent API for registering and executing health checks
    across various services (databases, caches, message queues, etc.). It supports
    method chaining for convenient configuration and returns detailed results for
    each check including execution time and status.
    
    Attributes:
        _checks (List[HealthCheck]): Internal list of registered health check functions.
    
    Example:
        Basic usage with multiple services:
        
        >>> health = Health()
        >>> health.redis_check("redis://localhost:6379") \\
        ...       .postgresql_check("postgresql://user:pass@localhost/db") \\
        ...       .mongodb_check("mongodb://localhost:27017")
        >>> results = health.run()
        >>> for result in results:
        ...     print(f"{result.name}: {result.status}")
        redis: healthy
        postgresql: healthy
        mongodb: healthy
        
        Using custom names for multiple instances:
        
        >>> health = Health()
        >>> health.redis_check("redis://primary:6379", name="redis-primary") \\
        ...       .redis_check("redis://cache:6379", name="redis-cache")
        >>> results = health.run()
        
        Custom health checks:
        
        >>> def custom_check():
        ...     return CheckResult("my-service", HealthStatus.healthy)
        >>> health = Health()
        >>> health.register(custom_check)
        >>> results = health.run()
    
    Methods:
        register(check): Register a custom health check function.
        run(): Execute all registered checks and return results.
        
        Built-in check methods:
        - Cache: redis_check(), keydb_check(), memcached_check()
        - Message Queue: rabbitmq_check()
        - Relational DB: postgresql_check(), mysql_check(), sqlite_check(), 
                        oracle_check(), mssql_check()
        - NoSQL DB: mongodb_check()
    
    Notes:
        - All check methods return self for method chaining.
        - Each check is executed independently; failures don't stop other checks.
        - Execution time is automatically measured for each check.
        - The 'name' parameter allows monitoring multiple instances of the same service.
    
    See Also:
        - CheckResult: Data class containing check results
        - HealthStatus: Enum defining health states (healthy, degraded, unhealthy)
        - overall_status(): Function to aggregate multiple check results
    """
    def __init__(self):
        self._checks: List[HealthCheck] = []

    # -----------------------------
    # Core registration
    # -----------------------------

    def register(self, check: HealthCheck) -> Health:
        """
        Register a health check function.
        """
        self._checks.append(check)
        return self  # enable chaining

    # -----------------------------
    # Built-in check helpers
    # -----------------------------

    def redis_check(self, redis_url: str, timeout: int = 2, name: str = "redis") -> Health:
        """
        Register a Redis health check.
        """
        from healthcheckx.checks.cache.redis_check import create_redis_check

        check = create_redis_check(redis_url, timeout, name)
        self.register(check)
        return self

    def keydb_check(self, keydb_url: str, timeout: int = 2, name: str = "keydb") -> Health:
        """
        Register a KeyDB health check.
        """
        from healthcheckx.checks.cache.keydb_check import create_keydb_check

        check = create_keydb_check(keydb_url, timeout, name)
        self.register(check)
        return self

    def memcached_check(self, host: str = "localhost", port: int = 11211, timeout: int = 2, name: str = "memcached") -> Health:
        """
        Register a Memcached health check.
        """
        from healthcheckx.checks.cache.memcached_check import create_memcached_check

        check = create_memcached_check(host, port, timeout, name)
        self.register(check)
        return self

    def rabbitmq_check(self, amqp_url: str, timeout: int = 2, name: str = "rabbitmq") -> Health:
        """
        Register a RabbitMQ health check.
        """
        from healthcheckx.checks.messageQueue.rabbitmq_check import create_rabbitmq_check

        check = create_rabbitmq_check(amqp_url, timeout, name)
        self.register(check)
        return self

    def postgresql_check(self, dsn: str, timeout: int = 3, name: str = "postgresql") -> Health:
        """
        Register a PostgreSQL health check.
        """
        from healthcheckx.checks.relationalDB.postgresql_check import create_postgresql_check

        check = create_postgresql_check(dsn, timeout, name)
        self.register(check)
        return self

    def mysql_check(self, dsn: str, timeout: int = 3, name: str = "mysql") -> Health:
        """
        Register a MySQL health check.
        """
        from healthcheckx.checks.relationalDB.mysql_check import create_mysql_check

        check = create_mysql_check(dsn, timeout, name)
        self.register(check)
        return self

    def sqlite_check(self, db_path: str, timeout: int = 3, name: str = "sqlite") -> Health:
        """
        Register a SQLite health check.
        """
        from healthcheckx.checks.relationalDB.sqlite_check import create_sqlite_check

        check = create_sqlite_check(db_path, timeout, name)
        self.register(check)
        return self

    def oracle_check(self, dsn: str, timeout: int = 3, name: str = "oracle") -> Health:
        """
        Register an Oracle health check.
        """
        from healthcheckx.checks.relationalDB.oracle_check import create_oracle_check

        check = create_oracle_check(dsn, timeout, name)
        self.register(check)
        return self

    def mssql_check(self, dsn: str, timeout: int = 3, name: str = "mssql") -> Health:
        """
        Register a MS SQL Server health check.
        """
        from healthcheckx.checks.relationalDB.mssql_check import create_mssql_check

        check = create_mssql_check(dsn, timeout, name)
        self.register(check)
        return self

    def mongodb_check(self, connection_string: str, timeout: int = 3, name: str = "mongodb") -> Health:
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

    def run(self) -> List[CheckResult]:
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

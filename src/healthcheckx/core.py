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
        
        Tests connectivity to a Redis server by executing a PING command.
        Supports standard Redis URL format including authentication.
        
        Args:
            redis_url: Redis connection URL (e.g., "redis://localhost:6379" or 
                      "redis://:password@localhost:6379/0")
            timeout: Connection timeout in seconds (default: 2)
            name: Name for this health check (default: "redis")
        
        Returns:
            Self for method chaining
        
        Example:
            >>> health = Health()
            >>> health.redis_check("redis://localhost:6379", name="redis-cache")
            >>> # With authentication
            >>> health.redis_check("redis://:mypassword@localhost:6379/1", name="redis-session")
        """
        from healthcheckx.checks.cache.redis_check import create_redis_check

        check = create_redis_check(redis_url, timeout, name)
        self.register(check)
        return self

    def keydb_check(self, keydb_url: str, timeout: int = 2, name: str = "keydb") -> Health:
        """
        Register a KeyDB health check.
        
        Tests connectivity to a KeyDB server (Redis-compatible) by executing a PING command.
        KeyDB is a high-performance fork of Redis with multithreading support.
        
        Args:
            keydb_url: KeyDB connection URL (e.g., "redis://localhost:6379" or
                      "redis://:password@localhost:6379/0")
            timeout: Connection timeout in seconds (default: 2)
            name: Name for this health check (default: "keydb")
        
        Returns:
            Self for method chaining
        
        Example:
            >>> health = Health()
            >>> health.keydb_check("redis://localhost:6379", name="keydb-primary")
            >>> # Multiple KeyDB instances
            >>> health.keydb_check("redis://keydb1:6379", name="keydb-shard1") \
            ...       .keydb_check("redis://keydb2:6379", name="keydb-shard2")
        """
        from healthcheckx.checks.cache.keydb_check import create_keydb_check

        check = create_keydb_check(keydb_url, timeout, name)
        self.register(check)
        return self

    def memcached_check(self, host: str = "localhost", port: int = 11211, timeout: int = 2, name: str = "memcached") -> Health:
        """
        Register a Memcached health check.
        
        Tests connectivity to a Memcached server by executing a version command.
        Memcached is a distributed memory caching system.
        
        Args:
            host: Memcached server hostname or IP address (default: "localhost")
            port: Memcached server port (default: 11211)
            timeout: Connection timeout in seconds (default: 2)
            name: Name for this health check (default: "memcached")
        
        Returns:
            Self for method chaining
        
        Example:
            >>> health = Health()
            >>> health.memcached_check("localhost", 11211, name="memcached-cache")
            >>> # Multiple Memcached servers
            >>> health.memcached_check("cache1.example.com", name="memcached-server1") \
            ...       .memcached_check("cache2.example.com", name="memcached-server2")
        """
        from healthcheckx.checks.cache.memcached_check import create_memcached_check

        check = create_memcached_check(host, port, timeout, name)
        self.register(check)
        return self

    def rabbitmq_check(self, amqp_url: str, timeout: int = 2, name: str = "rabbitmq") -> Health:
        """
        Register a RabbitMQ health check.
        
        Tests connectivity to a RabbitMQ server using AMQP protocol.
        Verifies the broker is accepting connections and can authenticate.
        
        Args:
            amqp_url: RabbitMQ connection URL using AMQP format
                     (e.g., "amqp://guest:guest@localhost:5672/%2F" or
                     "amqp://user:password@rabbitmq.example.com:5672/vhost")
            timeout: Connection timeout in seconds (default: 2)
            name: Name for this health check (default: "rabbitmq")
        
        Returns:
            Self for method chaining
        
        Example:
            >>> health = Health()
            >>> health.rabbitmq_check("amqp://guest:guest@localhost:5672/%2F", name="rabbitmq-broker")
            >>> # Production with custom vhost
            >>> health.rabbitmq_check("amqp://user:pass@rabbitmq:5672/production", name="rabbitmq-prod")
        """
        from healthcheckx.checks.messageQueue.rabbitmq_check import create_rabbitmq_check

        check = create_rabbitmq_check(amqp_url, timeout, name)
        self.register(check)
        return self

    def kafka_check(self, bootstrap_servers: str, timeout: int = 2, name: str = "kafka") -> Health:
        """
        Register a Kafka health check.
        
        Args:
            bootstrap_servers: Comma-separated list of Kafka broker addresses 
                             (e.g., "localhost:9092" or "broker1:9092,broker2:9092")
            timeout: Connection timeout in seconds (default: 2)
            name: Name for this health check (default: "kafka")
        
        Returns:
            Self for method chaining
        
        Example:
            >>> health = Health()
            >>> health.kafka_check("localhost:9092", name="kafka-broker")
            >>> # Multiple brokers
            >>> health.kafka_check("broker1:9092,broker2:9092", name="kafka-cluster")
        """
        from healthcheckx.checks.messageQueue.kafka_check import create_kafka_check

        check = create_kafka_check(bootstrap_servers, timeout, name)
        self.register(check)
        return self

    def activemq_check(self, broker_url: str, timeout: int = 2, name: str = "activemq") -> Health:
        """
        Register an ActiveMQ health check.
        
        Args:
            broker_url: ActiveMQ broker URL (e.g., "tcp://localhost:61616" or "stomp://localhost:61613")
            timeout: Connection timeout in seconds (default: 2)
            name: Name for this health check (default: "activemq")
        
        Returns:
            Self for method chaining
        
        Example:
            >>> health = Health()
            >>> health.activemq_check("tcp://localhost:61616", name="activemq-broker")
            >>> # Using STOMP protocol
            >>> health.activemq_check("stomp://localhost:61613", name="activemq-stomp")
        """
        from healthcheckx.checks.messageQueue.activemq_check import create_activemq_check

        check = create_activemq_check(broker_url, timeout, name)
        self.register(check)
        return self

    def postgresql_check(self, dsn: str, timeout: int = 3, name: str = "postgresql") -> Health:
        """
        Register a PostgreSQL health check.
        
        Tests connectivity to a PostgreSQL database by executing a simple query.
        Verifies database is accessible and accepting queries.
        
        Args:
            dsn: PostgreSQL connection string. Supports both formats:
                - URL format: "postgresql://user:password@localhost:5432/dbname"
                - Key-value format: "host=localhost port=5432 dbname=mydb user=postgres password=secret"
            timeout: Connection timeout in seconds (default: 3)
            name: Name for this health check (default: "postgresql")
        
        Returns:
            Self for method chaining
        
        Example:
            >>> health = Health()
            >>> health.postgresql_check("postgresql://user:pass@localhost:5432/mydb", name="postgres-main")
            >>> # Using DSN format
            >>> health.postgresql_check("host=db.example.com dbname=prod user=app", name="postgres-prod")
        """
        from healthcheckx.checks.relationalDB.postgresql_check import create_postgresql_check

        check = create_postgresql_check(dsn, timeout, name)
        self.register(check)
        return self

    def mysql_check(self, dsn: str, timeout: int = 3, name: str = "mysql") -> Health:
        """
        Register a MySQL health check.
        
        Tests connectivity to a MySQL/MariaDB database by executing a simple query.
        Supports both MySQL and MariaDB servers.
        
        Args:
            dsn: MySQL connection string. Supports URL format:
                - "mysql://user:password@localhost:3306/dbname"
                - "mysql://user:password@mysql.example.com/database?charset=utf8mb4"
            timeout: Connection timeout in seconds (default: 3)
            name: Name for this health check (default: "mysql")
        
        Returns:
            Self for method chaining
        
        Example:
            >>> health = Health()
            >>> health.mysql_check("mysql://root:password@localhost:3306/mydb", name="mysql-main")
            >>> # MariaDB with custom charset
            >>> health.mysql_check("mysql://user:pass@mariadb:3306/db?charset=utf8mb4", name="mariadb-prod")
        """
        from healthcheckx.checks.relationalDB.mysql_check import create_mysql_check

        check = create_mysql_check(dsn, timeout, name)
        self.register(check)
        return self

    def sqlite_check(self, db_path: str, timeout: int = 3, name: str = "sqlite") -> Health:
        """
        Register a SQLite health check.
        
        Tests connectivity to a SQLite database file by executing a simple query.
        Verifies the database file is accessible and not corrupted.
        
        Args:
            db_path: Path to the SQLite database file
                    (e.g., "/var/data/app.db" or "./local.sqlite3")
            timeout: Query timeout in seconds (default: 3)
            name: Name for this health check (default: "sqlite")
        
        Returns:
            Self for method chaining
        
        Example:
            >>> health = Health()
            >>> health.sqlite_check("/var/data/application.db", name="sqlite-main")
            >>> # Relative path
            >>> health.sqlite_check("./data/cache.db", name="sqlite-cache")
            >>> # In-memory database (special case)
            >>> health.sqlite_check(":memory:", name="sqlite-memory")
        """
        from healthcheckx.checks.relationalDB.sqlite_check import create_sqlite_check

        check = create_sqlite_check(db_path, timeout, name)
        self.register(check)
        return self

    def oracle_check(self, dsn: str, timeout: int = 3, name: str = "oracle") -> Health:
        """
        Register an Oracle health check.
        
        Tests connectivity to an Oracle database by executing a simple query.
        Supports Oracle Database 11g and later versions.
        
        Args:
            dsn: Oracle connection string. Supports multiple formats:
                - URL format: "oracle://user:password@localhost:1521/ORCL"
                - TNS format: "user/password@PROD_DB"
                - Full TNS: "user/password@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=host)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=ORCL)))"
            timeout: Connection timeout in seconds (default: 3)
            name: Name for this health check (default: "oracle")
        
        Returns:
            Self for method chaining
        
        Example:
            >>> health = Health()
            >>> health.oracle_check("oracle://system:password@localhost:1521/XE", name="oracle-xe")
            >>> # Using TNS format
            >>> health.oracle_check("user/pass@PROD_DB", name="oracle-prod")
            >>> # With service name
            >>> health.oracle_check("oracle://app:secret@oracledb:1521/ORCL", name="oracle-main")
        """
        from healthcheckx.checks.relationalDB.oracle_check import create_oracle_check

        check = create_oracle_check(dsn, timeout, name)
        self.register(check)
        return self

    def mssql_check(self, dsn: str, timeout: int = 3, name: str = "mssql") -> Health:
        """
        Register a MS SQL Server health check.
        
        Tests connectivity to a Microsoft SQL Server database by executing a simple query.
        Supports SQL Server 2012 and later versions.
        
        Args:
            dsn: MS SQL Server connection string in URL format:
                - "mssql://user:password@localhost:1433/database"
                - "mssql://sa:Password123@sqlserver.example.com/DatabaseName"
            timeout: Connection timeout in seconds (default: 3)
            name: Name for this health check (default: "mssql")
        
        Returns:
            Self for method chaining
        
        Example:
            >>> health = Health()
            >>> health.mssql_check("mssql://sa:Password@localhost:1433/master", name="mssql-local")
            >>> # With Windows authentication (may require additional config)
            >>> health.mssql_check("mssql://sqlserver/MyDatabase", name="mssql-windows")
            >>> # Azure SQL Database
            >>> health.mssql_check("mssql://user@server:pass@server.database.windows.net/db", name="azure-sql")
        """
        from healthcheckx.checks.relationalDB.mssql_check import create_mssql_check

        check = create_mssql_check(dsn, timeout, name)
        self.register(check)
        return self

    def mongodb_check(self, connection_string: str, timeout: int = 3, name: str = "mongodb") -> Health:
        """
        Register a MongoDB health check.
        
        Tests connectivity to a MongoDB server by executing a ping command.
        Supports MongoDB 3.6+ including replica sets and sharded clusters.
        
        Args:
            connection_string: MongoDB connection URI
                             (e.g., "mongodb://localhost:27017" or
                             "mongodb://user:password@mongodb.example.com:27017/database" or
                             "mongodb+srv://cluster.mongodb.net/database")
            timeout: Connection timeout in seconds (default: 3)
            name: Name for this health check (default: "mongodb")
        
        Returns:
            Self for method chaining
        
        Example:
            >>> health = Health()
            >>> health.mongodb_check("mongodb://localhost:27017", name="mongodb-local")
            >>> # With authentication
            >>> health.mongodb_check("mongodb://user:pass@mongo:27017/mydb", name="mongodb-app")
            >>> # MongoDB Atlas (cloud)
            >>> health.mongodb_check("mongodb+srv://user:pass@cluster.mongodb.net/db", name="mongodb-atlas")
            >>> # Replica set
            >>> health.mongodb_check("mongodb://host1:27017,host2:27017/db?replicaSet=rs0", name="mongodb-replica")
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

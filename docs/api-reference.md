# API Reference

Complete API documentation for healthcheckx.

## Core Classes

### `Health`

Main health check orchestrator.

```python
class Health:
    """
    Main health check orchestrator for monitoring service dependencies.
    
    The Health class provides a fluent API for registering and executing health checks
    across various services. It supports method chaining for convenient configuration.
    """
```

#### Methods

##### `register(check: HealthCheck) -> Health`

Register a custom health check function.

**Parameters:**
- `check` (HealthCheck): A callable that returns `CheckResult`

**Returns:**
- `Health`: Self for method chaining

**Example:**
```python
def custom_check():
    return CheckResult("my-service", HealthStatus.healthy)

health = Health()
health.register(custom_check)
```

##### `run() -> List[CheckResult]`

Execute all registered health checks.

**Returns:**
- `List[CheckResult]`: Results from all checks

**Example:**
```python
results = health.run()
for result in results:
    print(f"{result.name}: {result.status}")
```

---

### Cache Check Methods

##### `redis_check(redis_url: str, timeout: int = 2, name: str = "redis") -> Health`

Register a Redis health check.

Tests connectivity to a Redis server by executing a PING command. Supports standard Redis URL format including authentication.

**Parameters:**
- `redis_url` (str): Redis connection URL
  - Format: `redis://localhost:6379`
  - With auth: `redis://:password@localhost:6379/0`
  - With database: `redis://localhost:6379/1`
- `timeout` (int, optional): Connection timeout in seconds. Default: 2
- `name` (str, optional): Custom name for the check. Default: "redis"

**Examples:**
```python
# Basic
health.redis_check("redis://localhost:6379", name="redis-cache")

# With authentication
health.redis_check("redis://:mypassword@localhost:6379/1", name="redis-session")
```

##### `keydb_check(keydb_url: str, timeout: int = 2, name: str = "keydb") -> Health`

Register a KeyDB health check.

Tests connectivity to a KeyDB server (Redis-compatible) by executing a PING command. KeyDB is a high-performance fork of Redis with multithreading support.

**Parameters:**
- `keydb_url` (str): KeyDB connection URL (Redis format)
  - Format: `redis://localhost:6379`
  - With auth: `redis://:password@localhost:6379/0`
- `timeout` (int, optional): Connection timeout in seconds. Default: 2
- `name` (str, optional): Custom name for the check. Default: "keydb"

**Examples:**
```python
# Single instance
health.keydb_check("redis://localhost:6379", name="keydb-primary")

# Multiple KeyDB instances
health.keydb_check("redis://keydb1:6379", name="keydb-shard1") \
      .keydb_check("redis://keydb2:6379", name="keydb-shard2")
```

##### `memcached_check(host: str = "localhost", port: int = 11211, timeout: int = 2, name: str = "memcached") -> Health`

Register a Memcached health check.

Tests connectivity to a Memcached server by executing a version command. Memcached is a distributed memory caching system.

**Parameters:**
- `host` (str, optional): Memcached server hostname or IP address. Default: "localhost"
- `port` (int, optional): Memcached server port. Default: 11211
- `timeout` (int, optional): Connection timeout in seconds. Default: 2
- `name` (str, optional): Custom name for the check. Default: "memcached"

**Examples:**
```python
# Local server
health.memcached_check("localhost", 11211, name="memcached-cache")

# Multiple Memcached servers
health.memcached_check("cache1.example.com", name="memcached-server1") \
      .memcached_check("cache2.example.com", name="memcached-server2")
```

---

### Message Queue Check Methods

##### `rabbitmq_check(amqp_url: str, timeout: int = 2, name: str = "rabbitmq") -> Health`

Register a RabbitMQ health check.

Tests connectivity to a RabbitMQ server using AMQP protocol. Verifies the broker is accepting connections and can authenticate.

**Parameters:**
- `amqp_url` (str): RabbitMQ connection URL using AMQP format
  - Basic: `amqp://guest:guest@localhost:5672/%2F`
  - With vhost: `amqp://user:password@rabbitmq.example.com:5672/vhost`
- `timeout` (int, optional): Connection timeout in seconds. Default: 2
- `name` (str, optional): Custom name for the check. Default: "rabbitmq"

**Examples:**
```python
# Local instance
health.rabbitmq_check("amqp://guest:guest@localhost:5672/%2F", name="rabbitmq-broker")

# Production with custom vhost
health.rabbitmq_check("amqp://user:pass@rabbitmq:5672/production", name="rabbitmq-prod")
```

##### `kafka_check(bootstrap_servers: str, timeout: int = 2, name: str = "kafka") -> Health`

Register a Kafka health check.

Tests connectivity to Kafka brokers by attempting to retrieve cluster metadata.

**Parameters:**
- `bootstrap_servers` (str): Comma-separated list of Kafka broker addresses
  - Single broker: `localhost:9092`
  - Multiple brokers: `broker1:9092,broker2:9092`
- `timeout` (int, optional): Connection timeout in seconds. Default: 2
- `name` (str, optional): Custom name for the check. Default: "kafka"

**Examples:**
```python
# Single broker
health.kafka_check("localhost:9092", name="kafka-broker")

# Kafka cluster
health.kafka_check("broker1:9092,broker2:9092", name="kafka-cluster")
```

##### `activemq_check(broker_url: str, timeout: int = 2, name: str = "activemq") -> Health`

Register an ActiveMQ health check.

Tests connectivity to ActiveMQ broker using either TCP (OpenWire) or STOMP protocol, automatically detected from the URL.

**Parameters:**
- `broker_url` (str): ActiveMQ broker URL
  - TCP/OpenWire: `tcp://localhost:61616`
  - STOMP: `stomp://localhost:61613`
- `timeout` (int, optional): Connection timeout in seconds. Default: 2
- `name` (str, optional): Custom name for the check. Default: "activemq"

**Examples:**
```python
# OpenWire protocol (default port 61616)
health.activemq_check("tcp://localhost:61616", name="activemq-broker")

# STOMP protocol (default port 61613)
health.activemq_check("stomp://localhost:61613", name="activemq-stomp")
```

---

### Relational Database Check Methods

##### `postgresql_check(dsn: str, timeout: int = 3, name: str = "postgresql") -> Health`

Register a PostgreSQL health check.

Tests connectivity to a PostgreSQL database by executing a simple query. Verifies database is accessible and accepting queries.

**Parameters:**
- `dsn` (str): PostgreSQL connection string. Supports both formats:
  - URL format: `postgresql://user:password@localhost:5432/dbname`
  - Key-value format: `host=localhost port=5432 dbname=mydb user=postgres password=secret`
- `timeout` (int, optional): Connection timeout in seconds. Default: 3
- `name` (str, optional): Custom name for the check. Default: "postgresql"

**Examples:**
```python
# URL format
health.postgresql_check("postgresql://user:pass@localhost:5432/mydb", name="postgres-main")

# Key-value format
health.postgresql_check("host=db.example.com dbname=prod user=app", name="postgres-prod")
```

##### `mysql_check(dsn: str, timeout: int = 3, name: str = "mysql") -> Health`

Register a MySQL health check.

Tests connectivity to a MySQL/MariaDB database by executing a simple query. Supports both MySQL and MariaDB servers.

**Parameters:**
- `dsn` (str): MySQL connection string in URL format:
  - Basic: `mysql://user:password@localhost:3306/dbname`
  - With charset: `mysql://user:password@mysql.example.com/database?charset=utf8mb4`
- `timeout` (int, optional): Connection timeout in seconds. Default: 3
- `name` (str, optional): Custom name for the check. Default: "mysql"

**Examples:**
```python
# MySQL
health.mysql_check("mysql://root:password@localhost:3306/mydb", name="mysql-main")

# MariaDB with custom charset
health.mysql_check("mysql://user:pass@mariadb:3306/db?charset=utf8mb4", name="mariadb-prod")
```

##### `sqlite_check(db_path: str, timeout: int = 3, name: str = "sqlite") -> Health`

Register a SQLite health check.

Tests connectivity to a SQLite database file by executing a simple query. Verifies the database file is accessible and not corrupted.

**Parameters:**
- `db_path` (str): Path to the SQLite database file
  - File path: `/var/data/app.db` or `./local.sqlite3`
  - In-memory: `:memory:`
- `timeout` (int, optional): Query timeout in seconds. Default: 3
- `name` (str, optional): Custom name for the check. Default: "sqlite"

**Examples:**
```python
# Absolute path
health.sqlite_check("/var/data/application.db", name="sqlite-main")

# Relative path
health.sqlite_check("./data/cache.db", name="sqlite-cache")

# In-memory database
health.sqlite_check(":memory:", name="sqlite-memory")
```

##### `oracle_check(dsn: str, timeout: int = 3, name: str = "oracle") -> Health`

Register an Oracle health check.

Tests connectivity to an Oracle database by executing a simple query. Supports Oracle Database 11g and later versions.

**Parameters:**
- `dsn` (str): Oracle connection string. Supports multiple formats:
  - URL format: `oracle://user:password@localhost:1521/ORCL`
  - TNS format: `user/password@PROD_DB`
  - Full TNS: `user/password@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=host)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=ORCL)))`
- `timeout` (int, optional): Connection timeout in seconds. Default: 3
- `name` (str, optional): Custom name for the check. Default: "oracle"

**Examples:**
```python
# URL format
health.oracle_check("oracle://system:password@localhost:1521/XE", name="oracle-xe")

# TNS format
health.oracle_check("user/pass@PROD_DB", name="oracle-prod")

# With service name
health.oracle_check("oracle://app:secret@oracledb:1521/ORCL", name="oracle-main")
```

##### `mssql_check(dsn: str, timeout: int = 3, name: str = "mssql") -> Health`

Register a MS SQL Server health check.

Tests connectivity to a Microsoft SQL Server database by executing a simple query. Supports SQL Server 2012 and later versions.

**Parameters:**
- `dsn` (str): MS SQL Server connection string in URL format:
  - Basic: `mssql://user:password@localhost:1433/database`
  - With instance: `mssql://sa:Password123@sqlserver.example.com/DatabaseName`
- `timeout` (int, optional): Connection timeout in seconds. Default: 3
- `name` (str, optional): Custom name for the check. Default: "mssql"

**Examples:**
```python
# Local instance
health.mssql_check("mssql://sa:Password@localhost:1433/master", name="mssql-local")

# Azure SQL Database
health.mssql_check("mssql://user@server:pass@server.database.windows.net/db", name="azure-sql")
```

---

### NoSQL Database Check Methods

##### `mongodb_check(connection_string: str, timeout: int = 3, name: str = "mongodb") -> Health`

Register a MongoDB health check.

Tests connectivity to a MongoDB server by executing a ping command. Supports MongoDB 3.6+ including replica sets and sharded clusters.

**Parameters:**
- `connection_string` (str): MongoDB connection URI
  - Local: `mongodb://localhost:27017`
  - With auth: `mongodb://user:password@mongodb.example.com:27017/database`
  - Atlas: `mongodb+srv://cluster.mongodb.net/database`
  - Replica set: `mongodb://host1:27017,host2:27017/db?replicaSet=rs0`
- `timeout` (int, optional): Connection timeout in seconds. Default: 3
- `name` (str, optional): Custom name for the check. Default: "mongodb"

**Examples:**
```python
# Local instance
health.mongodb_check("mongodb://localhost:27017", name="mongodb-local")

# With authentication
health.mongodb_check("mongodb://user:pass@mongo:27017/mydb", name="mongodb-app")

# MongoDB Atlas (cloud)
health.mongodb_check("mongodb+srv://user:pass@cluster.mongodb.net/db", name="mongodb-atlas")

# Replica set
health.mongodb_check("mongodb://host1:27017,host2:27017/db?replicaSet=rs0", name="mongodb-replica")
```

---

## Data Classes

### `CheckResult`

Contains the result of a health check.

```python
@dataclass
class CheckResult:
    name: str                      # Name/identifier of the check
    status: HealthStatus          # Health status
    message: Optional[str] = None # Optional error/status message
    duration_ms: Optional[float] = None  # Execution time in milliseconds
```

**Attributes:**
- `name` (str): Unique identifier for the health check
- `status` (HealthStatus): The health status (healthy/degraded/unhealthy)
- `message` (Optional[str]): Additional information, typically error messages
- `duration_ms` (Optional[float]): How long the check took to execute

**Example:**
```python
result = CheckResult(
    name="redis",
    status=HealthStatus.healthy,
    message=None,
    duration_ms=12.5
)
```

---

## Enums

### `HealthStatus`

Enumeration of possible health states.

```python
class HealthStatus(str, Enum):
    healthy = "healthy"      # Service is functioning normally
    degraded = "degraded"    # Service is operational but impaired
    unhealthy = "unhealthy"  # Service is down or failing
```

**Values:**
- `healthy`: Service is functioning normally
- `degraded`: Service is operational but with reduced functionality
- `unhealthy`: Service is completely down or failing

**Example:**
```python
from healthcheckx import HealthStatus

if result.status == HealthStatus.healthy:
    print("All systems operational")
elif result.status == HealthStatus.degraded:
    print("Service degraded")
else:
    print("Service down")
```

---

## Functions

### `overall_status(results: List[CheckResult]) -> HealthStatus`

Determine overall health status from multiple check results.

**Parameters:**
- `results` (List[CheckResult]): List of check results

**Returns:**
- `HealthStatus`: Aggregated status

**Logic:**
- If ANY check is `unhealthy` → Returns `unhealthy`
- Else if ANY check is `degraded` → Returns `degraded`
- Else → Returns `healthy`

**Example:**
```python
from healthcheckx import Health, overall_status

health = Health()
health.redis_check("redis://localhost:6379")
health.postgresql_check("postgresql://localhost/db")

results = health.run()
status = overall_status(results)

print(f"Overall Status: {status}")
```

---

## Type Aliases

### `HealthCheck`

Type alias for health check callables.

```python
HealthCheck = Callable[[], CheckResult]
```

A health check is any callable that takes no parameters and returns a `CheckResult`.

**Example:**
```python
def my_check() -> CheckResult:
    return CheckResult("my-service", HealthStatus.healthy)

# my_check matches the HealthCheck type
```

---

## Framework Adapters

### `FastAPIAdapter`

Adapter for integrating with FastAPI applications.

```python
from healthcheckx import Health, FastAPIAdapter

health = Health()
health.redis_check("redis://localhost:6379")

adapter = FastAPIAdapter(health)
app.get("/health")(adapter.endpoint)
```

**HTTP Response:**
- Status Code: 200 (healthy/degraded) or 503 (unhealthy)
- Content-Type: application/json

### `flask_health_endpoint(health: Health)`

Create a Flask view function for health checks.

```python
from healthcheckx import Health, flask_health_endpoint

health = Health()
health.redis_check("redis://localhost:6379")

app.route("/health")(flask_health_endpoint(health))
```

### `django_health_view(health: Health)`

Create a Django view function for health checks.

```python
from healthcheckx import Health, django_health_view

health = Health()
health.redis_check("redis://localhost:6379")

urlpatterns = [
    path('health/', django_health_view(health)),
]
```

---

## Constants

### Version

```python
import healthcheckx
print(healthcheckx.__version__)  # e.g., "0.1.2"
```

---

## Complete Example

```python
from healthcheckx import (
    Health,
    CheckResult,
    HealthStatus,
    overall_status
)

# Create health instance
health = Health()

# Register multiple checks
health.redis_check("redis://localhost:6379", timeout=2, name="redis-cache") \
      .postgresql_check("postgresql://user:pass@localhost/db", timeout=3) \
      .mongodb_check("mongodb://localhost:27017", timeout=3)

# Custom check
def api_check() -> CheckResult:
    try:
        # Your check logic
        return CheckResult("external-api", HealthStatus.healthy)
    except Exception as e:
        return CheckResult("external-api", HealthStatus.unhealthy, str(e))

health.register(api_check)

# Execute all checks
results = health.run()

# Get overall status
status = overall_status(results)

# Process results
for result in results:
    print(f"{result.name}: {result.status} ({result.duration_ms:.2f}ms)")
    if result.message:
        print(f"  Message: {result.message}")

print(f"\nOverall: {status}")
```

## See Also

- [Quick Start Guide](quickstart.md)
- [Built-in Checks](checks/cache.md)
- [Custom Checks](advanced/custom-checks.md)
- [Examples](examples.md)

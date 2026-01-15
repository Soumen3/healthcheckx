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

**Parameters:**
- `redis_url` (str): Redis connection URL (e.g., "redis://localhost:6379")
- `timeout` (int, optional): Connection timeout in seconds. Default: 2
- `name` (str, optional): Custom name for the check. Default: "redis"

**Example:**
```python
health.redis_check("redis://localhost:6379", timeout=3, name="redis-cache")
```

##### `keydb_check(keydb_url: str, timeout: int = 2, name: str = "keydb") -> Health`

Register a KeyDB health check.

**Parameters:**
- `keydb_url` (str): KeyDB connection URL (e.g., "keydb://localhost:6379")
- `timeout` (int, optional): Connection timeout in seconds. Default: 2
- `name` (str, optional): Custom name for the check. Default: "keydb"

##### `memcached_check(host: str = "localhost", port: int = 11211, timeout: int = 2, name: str = "memcached") -> Health`

Register a Memcached health check.

**Parameters:**
- `host` (str, optional): Memcached server host. Default: "localhost"
- `port` (int, optional): Memcached server port. Default: 11211
- `timeout` (int, optional): Connection timeout in seconds. Default: 2
- `name` (str, optional): Custom name for the check. Default: "memcached"

---

### Message Queue Check Methods

##### `rabbitmq_check(amqp_url: str, timeout: int = 2, name: str = "rabbitmq") -> Health`

Register a RabbitMQ health check.

**Parameters:**
- `amqp_url` (str): AMQP connection URL (e.g., "amqp://guest:guest@localhost:5672")
- `timeout` (int, optional): Connection timeout in seconds. Default: 2
- `name` (str, optional): Custom name for the check. Default: "rabbitmq"

---

### Relational Database Check Methods

##### `postgresql_check(dsn: str, timeout: int = 3, name: str = "postgresql") -> Health`

Register a PostgreSQL health check.

**Parameters:**
- `dsn` (str): PostgreSQL connection string (e.g., "postgresql://user:pass@localhost/db")
- `timeout` (int, optional): Connection timeout in seconds. Default: 3
- `name` (str, optional): Custom name for the check. Default: "postgresql"

##### `mysql_check(dsn: str, timeout: int = 3, name: str = "mysql") -> Health`

Register a MySQL health check.

**Parameters:**
- `dsn` (str): MySQL connection string (e.g., "mysql://user:pass@localhost:3306/db")
- `timeout` (int, optional): Connection timeout in seconds. Default: 3
- `name` (str, optional): Custom name for the check. Default: "mysql"

##### `sqlite_check(db_path: str, timeout: int = 3, name: str = "sqlite") -> Health`

Register a SQLite health check.

**Parameters:**
- `db_path` (str): Path to SQLite database file (e.g., "/path/to/db.db" or ":memory:")
- `timeout` (int, optional): Connection timeout in seconds. Default: 3
- `name` (str, optional): Custom name for the check. Default: "sqlite"

##### `oracle_check(dsn: str, timeout: int = 3, name: str = "oracle") -> Health`

Register an Oracle health check.

**Parameters:**
- `dsn` (str): Oracle connection string (e.g., "oracle://user:pass@localhost:1521/service")
- `timeout` (int, optional): Connection timeout in seconds. Default: 3
- `name` (str, optional): Custom name for the check. Default: "oracle"

##### `mssql_check(dsn: str, timeout: int = 3, name: str = "mssql") -> Health`

Register a MS SQL Server health check.

**Parameters:**
- `dsn` (str): MS SQL connection string (e.g., "mssql://user:pass@localhost:1433/db")
- `timeout` (int, optional): Connection timeout in seconds. Default: 3
- `name` (str, optional): Custom name for the check. Default: "mssql"

---

### NoSQL Database Check Methods

##### `mongodb_check(connection_string: str, timeout: int = 3, name: str = "mongodb") -> Health`

Register a MongoDB health check.

**Parameters:**
- `connection_string` (str): MongoDB connection string (e.g., "mongodb://localhost:27017")
- `timeout` (int, optional): Connection timeout in seconds. Default: 3
- `name` (str, optional): Custom name for the check. Default: "mongodb"

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

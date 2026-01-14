# healthcheckx

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**healthcheckx** is a production-grade health check library for Python applications. It provides a simple, extensible framework for monitoring the health of various services and components in your application.

## 🚀 Features

- **🔌 Framework Agnostic**: Core library works independently, with optional adapters for FastAPI, Flask, and Django
- **🎯 Built-in Health Checks**: Pre-built checks for popular services (Redis, KeyDB, Memcached, RabbitMQ, PostgreSQL, MySQL, SQLite, Oracle, MS SQL Server, MongoDB)
- **⚡ Simple & Extensible**: Easy to add custom health checks with a clean API
- **🏷️ Named Checks**: Support for multiple instances of the same service with custom names
- **🎭 Graceful Degradation**: Distinguishes between healthy, degraded, and unhealthy states
- **⏱️ Performance Tracking**: Measures execution time for each health check
- **🛡️ Error Handling**: Catches exceptions gracefully and returns meaningful status
- **🔧 Configurable Timeouts**: Non-blocking checks with configurable timeouts
- **📦 Optional Dependencies**: Install only what you need

## 📦 Installation

### Basic Installation

```bash
pip install healthcheckx
```

### With Optional Dependencies

Install support for specific services:

```bash
# Redis support (also works for KeyDB)
pip install healthcheckx[redis]

# Memcached support
pip install healthcheckx[memcached]

# RabbitMQ support
pip install healthcheckx[rabbitmq]

# PostgreSQL support
pip install healthcheckx[postgresql]

# MySQL support
pip install healthcheckx[mysql]

# SQLite (built-in, no extra dependencies needed)

# Oracle support
pip install healthcheckx[oracle]

# MS SQL Server support
pip install healthcheckx[mssql]

# MongoDB support
pip install healthcheckx[mongodb]

# Install everything
pip install healthcheckx[all]
```

## 🎯 Quick Start

### Basic Usage

```python
from healthcheckx import Health

# Create health check instance
health = Health()

# Register built-in checks (method chaining supported)
health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://user:pass@localhost/db") \
      .mongodb_check("mongodb://localhost:27017")

# Run all checks
results = health.run()

# Inspect results
for result in results:
    print(f"{result.name}: {result.status} ({result.duration_ms:.2f}ms)")
    if result.message:
        print(f"  Message: {result.message}")
```

### Aggregate Status

```python
from healthcheckx import Health, overall_status

health = Health()
health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://user:pass@localhost/db")

results = health.run()
status = overall_status(results)  # Returns: "healthy", "degraded", or "unhealthy"

print(f"Overall Status: {status}")
```

## 🔧 Built-in Health Checks

### Cache Systems

#### Redis

```python
health.redis_check("redis://localhost:6379", timeout=2)

# With custom name (for multiple Redis instances)
health.redis_check("redis://primary.local:6379", timeout=2, name="redis-primary")
health.redis_check("redis://secondary.local:6379", timeout=2, name="redis-secondary")
```

#### KeyDB

```python
# KeyDB is Redis-compatible
health.keydb_check("keydb://localhost:6379", timeout=2)

# Can also use redis:// scheme
health.keydb_check("redis://localhost:6379", timeout=2)

# With authentication
health.keydb_check("keydb://user:password@localhost:6379/0", name="keydb")
```

#### Memcached

```python
# Basic usage
health.memcached_check()

# With custom host and port
health.memcached_check(host="localhost", port=11211, timeout=2)

# Multiple Memcached instances
health.memcached_check(host="cache1.local", port=11211, name="memcached-1")
health.memcached_check(host="cache2.local", port=11211, name="memcached-2")
```

### Message Queues

#### RabbitMQ

```python
health.rabbitmq_check("amqp://guest:guest@localhost:5672", timeout=2)
```

### Relational Databases

#### PostgreSQL

```python
health.postgresql_check("postgresql://user:password@localhost:5432/mydb", timeout=3)

# Multiple PostgreSQL databases
health.postgresql_check("postgresql://user:pass@db1:5432/app", name="postgres-main")
health.postgresql_check("postgresql://user:pass@db2:5432/analytics", name="postgres-analytics")
```

#### MySQL

```python
health.mysql_check("mysql://root:password@localhost:3306/mydb", timeout=3)

# Multiple MySQL databases with custom names
health.mysql_check("mysql://user:pass@localhost:3306/users", name="mysql-users-db")
health.mysql_check("mysql://user:pass@localhost:3306/orders", name="mysql-orders-db")
```

#### SQLite

```python
# File-based database
health.sqlite_check("/path/to/database.db", timeout=3)

# In-memory database
health.sqlite_check(":memory:")
```

#### Oracle

```python
# URL format
health.oracle_check("oracle://user:password@localhost:1521/XEPDB1", timeout=3)

# TNS format
health.oracle_check("user/password@localhost:1521/service_name")
```

#### MS SQL Server

```python
health.mssql_check("mssql://sa:Password@localhost:1433/master", timeout=3)
```

### NoSQL Databases

#### MongoDB

```python
# Local MongoDB
health.mongodb_check("mongodb://localhost:27017", timeout=3)

# With authentication
health.mongodb_check("mongodb://user:password@localhost:27017/mydb")

# MongoDB Atlas (cloud)
health.mongodb_check("mongodb+srv://user:pass@cluster.mongodb.net/db")
```

## 🌐 Framework Integration

### FastAPI

```python
from fastapi import FastAPI
from healthcheckx import Health, FastAPIAdapter

app = FastAPI()
health = Health()

# Register health checks
health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://user:pass@localhost/db")

# Add health endpoint
adapter = FastAPIAdapter(health)
app.get("/health")(adapter.endpoint)

# Returns:
# - HTTP 200 for healthy/degraded
# - HTTP 503 for unhealthy
# - JSON body with status and individual check results
```

**Response Example:**
```json
{
  "status": "healthy",
  "checks": [
    {
      "name": "redis",
      "status": "healthy",
      "duration_ms": 12.5
    },
    {
      "name": "postgresql",
      "status": "healthy",
      "duration_ms": 45.3
    }
  ]
}
```

### Flask

```python
from flask import Flask
from healthcheckx import Health, flask_health_endpoint

app = Flask(__name__)
health = Health()

# Register health checks
health.redis_check("redis://localhost:6379") \
      .mysql_check("mysql://root:pass@localhost:3306/db")

# Add health endpoint
app.route("/health")(flask_health_endpoint(health))
```

### Django

```python
# urls.py
from django.urls import path
from healthcheckx import Health, django_health_view

health = Health()
health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://user:pass@localhost/db")

urlpatterns = [
    path('health/', django_health_view(health)),
]
```

## 🎨 Custom Health Checks

### Creating Custom Checks

You can create custom health checks by defining a function that returns a `CheckResult`:

```python
from healthcheckx import Health, CheckResult, HealthStatus

def custom_api_check():
    """Check external API availability"""
    try:
        import requests
        response = requests.get("https://api.example.com/status", timeout=2)
        
        if response.status_code == 200:
            return CheckResult("external-api", HealthStatus.healthy)
        else:
            return CheckResult(
                "external-api", 
                HealthStatus.degraded,
                f"API returned {response.status_code}"
            )
    except Exception as e:
        return CheckResult(
            "external-api",
            HealthStatus.unhealthy,
            str(e)
        )

# Register custom check
health = Health()
health.register(custom_api_check)
results = health.run()
```

### Reusable Custom Checks (Factory Pattern)

```python
def create_disk_check(path: str, min_free_percent: float = 10.0):
    """Factory function to create disk space check"""
    def check():
        import shutil
        stat = shutil.disk_usage(path)
        free_percent = (stat.free / stat.total) * 100
        
        if free_percent >= min_free_percent:
            return CheckResult("disk", HealthStatus.healthy)
        elif free_percent >= min_free_percent / 2:
            return CheckResult(
                "disk",
                HealthStatus.degraded,
                f"Low disk space: {free_percent:.1f}% free"
            )
        else:
            return CheckResult(
                "disk",
                HealthStatus.unhealthy,
                f"Critical disk space: {free_percent:.1f}% free"
            )
    
    return check

# Use the custom check
health = Health()
health.register(create_disk_check("/", min_free_percent=15.0))
results = health.run()
```

### HTTP Service Check Example

```python
def create_http_check(url: str, timeout: int = 3):
    """Check HTTP endpoint availability"""
    def check():
        try:
            import requests
            response = requests.get(url, timeout=timeout)
            
            if response.status_code == 200:
                return CheckResult("http-check", HealthStatus.healthy)
            else:
                return CheckResult(
                    "http-check",
                    HealthStatus.unhealthy,
                    f"HTTP {response.status_code}"
                )
        except Exception as e:
            return CheckResult("http-check", HealthStatus.unhealthy, str(e))
    
    return check

health = Health()
health.register(create_http_check("https://api.example.com/ping"))
```

## 📊 Health Status Levels

healthcheckx supports three levels of health status:

1. **`healthy`**: Service is functioning normally
2. **`degraded`**: Service is operational but impaired (e.g., high latency, partial functionality)
3. **`unhealthy`**: Service is down or failing

### Aggregation Rules

When determining overall status from multiple checks:

- If **any** check is `unhealthy` → Overall status is `unhealthy`
- Else if **any** check is `degraded` → Overall status is `degraded`
- Else → Overall status is `healthy`

## ⚙️ API Reference

### `Health` Class

#### Methods

- **`register(check: Callable) -> Health`**: Register a health check function
- **`run() -> List[CheckResult]`**: Execute all registered checks and return results

**Cache Checks:**
- **`redis_check(redis_url: str, timeout: int = 2, name: str = "redis") -> Health`**: Register Redis check
- **`keydb_check(keydb_url: str, timeout: int = 2, name: str = "keydb") -> Health`**: Register KeyDB check
- **`memcached_check(host: str = "localhost", port: int = 11211, timeout: int = 2, name: str = "memcached") -> Health`**: Register Memcached check

**Message Queue Checks:**
- **`rabbitmq_check(amqp_url: str, timeout: int = 2, name: str = "rabbitmq") -> Health`**: Register RabbitMQ check

**Relational Database Checks:**
- **`postgresql_check(dsn: str, timeout: int = 3, name: str = "postgresql") -> Health`**: Register PostgreSQL check
- **`mysql_check(dsn: str, timeout: int = 3, name: str = "mysql") -> Health`**: Register MySQL check
- **`sqlite_check(db_path: str, timeout: int = 3, name: str = "sqlite") -> Health`**: Register SQLite check
- **`oracle_check(dsn: str, timeout: int = 3, name: str = "oracle") -> Health`**: Register Oracle check
- **`mssql_check(dsn: str, timeout: int = 3, name: str = "mssql") -> Health`**: Register MS SQL Server check

**NoSQL Database Checks:**
- **`mongodb_check(connection_string: str, timeout: int = 3, name: str = "mongodb") -> Health`**: Register MongoDB check

### `CheckResult` Class

```python
@dataclass
class CheckResult:
    name: str                    # Name/identifier of the check
    status: HealthStatus         # Health status (healthy/degraded/unhealthy)
    message: str | None = None   # Optional message (usually for errors)
    duration_ms: float | None = None  # Execution time in milliseconds
```

### `HealthStatus` Enum

```python
class HealthStatus(str, Enum):
    healthy = "healthy"
    degraded = "degraded"
    unhealthy = "unhealthy"
```

### `overall_status()` Function

```python
def overall_status(results: List[CheckResult]) -> HealthStatus:
    """Determine overall health status from individual check results"""
```

## 🛠️ Advanced Usage

### Conditional Health Checks

```python
import os
from healthcheckx import Health

health = Health()

# Always check database
health.postgresql_check(os.getenv("DATABASE_URL"))

# Only check Redis in production
if os.getenv("ENV") == "production":
    health.redis_check(os.getenv("REDIS_URL"))
```

### Dynamic Check Registration

```python
databases = [
    {"type": "postgresql", "dsn": "postgresql://localhost/db1"},
    {"type": "mysql", "dsn": "mysql://localhost/db2"},
]

health = Health()
for db in databases:
    if db["type"] == "postgresql":
        health.postgresql_check(db["dsn"])
    elif db["type"] == "mysql":
        health.mysql_check(db["dsn"])
```

### Custom Timeout Configuration

```python
health = Health()

# Different timeouts for different services
health.redis_check("redis://localhost:6379", timeout=1)  # Fast check
health.postgresql_check("postgresql://localhost/db", timeout=5)  # Slower check
health.mongodb_check("mongodb://localhost:27017", timeout=3)  # Medium check
```

### Multiple Instances of Same Service

Use the `name` parameter to monitor multiple instances of the same service:

```python
health = Health()

# Multiple Redis instances
health.redis_check("redis://primary:6379", name="redis-primary") \
      .redis_check("redis://cache:6379", name="redis-cache") \
      .redis_check("redis://sessions:6379", name="redis-sessions")

# Multiple databases
health.postgresql_check("postgresql://db1/users", name="users-db") \
      .postgresql_check("postgresql://db2/orders", name="orders-db") \
      .mysql_check("mysql://db3/analytics", name="analytics-db")

# Multiple Memcached servers
health.memcached_check(host="cache1", port=11211, name="cache-node-1") \
      .memcached_check(host="cache2", port=11211, name="cache-node-2")

results = health.run()

# Each check has its unique name
for result in results:
    print(f"{result.name}: {result.status}")
# Output:
# redis-primary: healthy
# redis-cache: healthy
# redis-sessions: healthy
# users-db: healthy
# orders-db: healthy
# analytics-db: healthy
# cache-node-1: healthy
# cache-node-2: healthy
```

### Health Check with Environment Variables

```python
import os
from healthcheckx import Health

health = Health()

# Load from environment
if redis_url := os.getenv("REDIS_URL"):
    health.redis_check(redis_url)

if db_url := os.getenv("DATABASE_URL"):
    health.postgresql_check(db_url)

if mongodb_url := os.getenv("MONGODB_URL"):
    health.mongodb_check(mongodb_url)
```

## 🧪 Testing Your Application

```python
from healthcheckx import Health, HealthStatus

def test_application_health():
    health = Health()
    health.postgresql_check("postgresql://localhost/test_db")
    health.redis_check("redis://localhost:6379")
    
    results = health.run()
    
    # Assert all checks passed
    for result in results:
        assert result.status == HealthStatus.healthy
        assert result.duration_ms < 1000  # All checks under 1 second
```

## 🐳 Docker Health Checks

Use healthcheckx in Docker health checks:

```dockerfile
FROM python:3.11
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔍 Monitoring & Observability

Integrate with monitoring tools:

```python
from healthcheckx import Health, HealthStatus
import logging

health = Health()
health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://localhost/db")

results = health.run()

# Log results
for result in results:
    if result.status == HealthStatus.unhealthy:
        logging.error(f"{result.name} is unhealthy: {result.message}")
    elif result.status == HealthStatus.degraded:
        logging.warning(f"{result.name} is degraded: {result.message}")

# Send to metrics system (Prometheus, etc.)
for result in results:
    # metrics.gauge(f"health.{result.name}.duration_ms", result.duration_ms)
    # metrics.gauge(f"health.{result.name}.status", 1 if result.status == "healthy" else 0)
    pass
```

## 📝 Best Practices

1. **Set Appropriate Timeouts**: Keep health check timeouts short (2-5 seconds) to avoid blocking
2. **Use Named Checks**: When monitoring multiple instances, use the `name` parameter to distinguish them
3. **Separate Readiness from Liveness**: Use different health check endpoints for Kubernetes readiness/liveness probes
4. **Cache Results**: For high-traffic endpoints, consider caching health check results for a few seconds
5. **Monitor Check Duration**: Track `duration_ms` to identify slow dependencies
6. **Use Graceful Degradation**: Return `degraded` status when service is operational but impaired
7. **Avoid Heavy Operations**: Health checks should be lightweight (simple ping/select operations)
8. **Handle Exceptions**: Let healthcheckx handle exceptions gracefully by returning appropriate status

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Homepage**: [https://github.com/Soumen3/healthcheckx](https://github.com/Soumen3/healthcheckx)
- **Issues**: [https://github.com/Soumen3/healthcheckx/issues](https://github.com/Soumen3/healthcheckx/issues)
- **PyPI**: [https://pypi.org/project/healthcheckx/](https://pypi.org/project/healthcheckx/)

## 👨‍💻 Author

**Soumen Samanta**

---

Made with ❤️ for the Python community

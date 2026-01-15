# Configuration

Configure health check behavior including timeouts, retries, and custom settings.

## Overview

healthcheckx provides sensible defaults but allows you to customize:

- Connection timeouts
- Check behavior
- Error handling
- Response formats
- Execution strategies

## Default Settings

All built-in checks use these defaults:

```python
DEFAULT_TIMEOUT = 2  # seconds
DEFAULT_CONNECT_TIMEOUT = 2  # seconds
```

## Connection Strings

### Redis

```python
health.redis_check("redis://localhost:6379/0", name="redis")

# With password
health.redis_check("redis://:password@localhost:6379/0", name="redis")

# With username and password (Redis 6+)
health.redis_check("redis://user:password@localhost:6379/0", name="redis")

# SSL/TLS
health.redis_check("rediss://localhost:6380/0", name="redis-ssl")
```

### PostgreSQL

```python
# Basic
health.postgresql_check(
    "postgresql://user:password@localhost:5432/dbname",
    name="postgres"
)

# With SSL
health.postgresql_check(
    "postgresql://user:password@localhost:5432/dbname?sslmode=require",
    name="postgres"
)

# Custom timeout in connection string
health.postgresql_check(
    "postgresql://user:password@localhost:5432/dbname?connect_timeout=5",
    name="postgres"
)
```

### MySQL

```python
# Basic
health.mysql_check(
    "mysql://user:password@localhost:3306/dbname",
    name="mysql"
)

# With charset
health.mysql_check(
    "mysql://user:password@localhost:3306/dbname?charset=utf8mb4",
    name="mysql"
)
```

### MongoDB

```python
# Basic
health.mongodb_check(
    "mongodb://localhost:27017/dbname",
    name="mongodb"
)

# With authentication
health.mongodb_check(
    "mongodb://user:password@localhost:27017/dbname?authSource=admin",
    name="mongodb"
)

# Replica set
health.mongodb_check(
    "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/dbname?replicaSet=rs0",
    name="mongodb"
)

# With timeout
health.mongodb_check(
    "mongodb://localhost:27017/dbname?serverSelectionTimeoutMS=2000",
    name="mongodb"
)
```

### RabbitMQ

```python
# Basic
health.rabbitmq_check(
    "amqp://guest:guest@localhost:5672/",
    name="rabbitmq"
)

# Virtual host
health.rabbitmq_check(
    "amqp://user:password@localhost:5672/myvhost",
    name="rabbitmq"
)

# SSL
health.rabbitmq_check(
    "amqps://user:password@localhost:5671/",
    name="rabbitmq-ssl"
)
```

### Memcached

```python
# Single server
health.memcached_check(
    "memcached://localhost:11211",
    name="memcached"
)

# Multiple servers (client handles distribution)
health.memcached_check(
    "memcached://cache1:11211,cache2:11211",
    name="memcached-cluster"
)
```

### KeyDB

```python
# Same as Redis
health.keydb_check("redis://localhost:6379", name="keydb")
```

### SQLite

```python
# File-based
health.sqlite_check("sqlite:///path/to/database.db", name="sqlite")

# Absolute path
health.sqlite_check("sqlite:////absolute/path/to/database.db", name="sqlite")

# In-memory (for testing)
health.sqlite_check("sqlite:///:memory:", name="sqlite-memory")
```

### Oracle

```python
# TNS format
health.oracle_check(
    "oracle://user:password@localhost:1521/ORCL",
    name="oracle"
)

# Easy Connect format
health.oracle_check(
    "oracle://user:password@//localhost:1521/service_name",
    name="oracle"
)
```

### MS SQL Server

```python
# Basic
health.mssql_check(
    "mssql://user:password@localhost:1433/dbname",
    name="mssql"
)

# Windows Authentication
health.mssql_check(
    "mssql://localhost:1433/dbname?trusted_connection=yes",
    name="mssql"
)
```

## Environment Variables

Best practice: Use environment variables for configuration:

```python
from healthcheckx import Health
import os

def create_health():
    health = Health()
    
    # Get from environment with defaults
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    db_url = os.getenv("DATABASE_URL", "postgresql://localhost/mydb")
    
    health.redis_check(redis_url, name="redis")
    health.postgresql_check(db_url, name="database")
    
    return health

health = create_health()
```

### Environment File (.env)

```bash
# .env file
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
REDIS_URL=redis://:password@localhost:6379/0
RABBITMQ_URL=amqp://user:pass@localhost:5672/
MONGODB_URL=mongodb://localhost:27017/mydb
```

Load with python-dotenv:

```python
from healthcheckx import Health
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

health = Health()

health.postgresql_check(os.getenv("DATABASE_URL"), name="database")
health.redis_check(os.getenv("REDIS_URL"), name="redis")
health.rabbitmq_check(os.getenv("RABBITMQ_URL"), name="rabbitmq")
health.mongodb_check(os.getenv("MONGODB_URL"), name="mongodb")
```

## Configuration Classes

Create configuration classes for better organization:

```python
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class RedisConfig:
    url: str
    name: str = "redis"
    
    @classmethod
    def from_env(cls, env_var: str = "REDIS_URL", name: str = "redis"):
        return cls(
            url=os.getenv(env_var, "redis://localhost:6379"),
            name=name
        )

@dataclass
class DatabaseConfig:
    url: str
    name: str = "database"
    
    @classmethod
    def from_env(cls, env_var: str = "DATABASE_URL", name: str = "database"):
        return cls(
            url=os.getenv(env_var, "postgresql://localhost/mydb"),
            name=name
        )

@dataclass
class HealthConfig:
    redis: RedisConfig
    database: DatabaseConfig
    rabbitmq_url: Optional[str] = None
    
    @classmethod
    def from_env(cls):
        return cls(
            redis=RedisConfig.from_env(),
            database=DatabaseConfig.from_env(),
            rabbitmq_url=os.getenv("RABBITMQ_URL")
        )

# Usage
config = HealthConfig.from_env()

health = Health()
health.redis_check(config.redis.url, name=config.redis.name)
health.postgresql_check(config.database.url, name=config.database.name)

if config.rabbitmq_url:
    health.rabbitmq_check(config.rabbitmq_url, name="rabbitmq")
```

## Custom Timeout Configuration

For custom checks with specific timeouts:

```python
from healthcheckx import Health, CheckResult, HealthStatus
import requests

def create_api_check(url: str, timeout: int = 2):
    """Factory with custom timeout"""
    def check() -> CheckResult:
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                return CheckResult("api", HealthStatus.healthy)
            return CheckResult("api", HealthStatus.unhealthy, f"HTTP {response.status_code}")
        except Exception as e:
            return CheckResult("api", HealthStatus.unhealthy, str(e))
    return check

health = Health()

# Different timeouts for different services
health.register(create_api_check("https://fast-api.com", timeout=1))
health.register(create_api_check("https://slow-api.com", timeout=5))
```

## Logging Configuration

Configure logging for health checks:

```python
from healthcheckx import Health
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

health = Health()
health.redis_check("redis://localhost:6379", name="redis")
health.postgresql_check("postgresql://localhost/db", name="database")

# Log results
results = health.run()
for result in results:
    if result.status.value == "unhealthy":
        logger.error(f"{result.name} is unhealthy: {result.message}")
    elif result.status.value == "degraded":
        logger.warning(f"{result.name} is degraded: {result.message}")
    else:
        logger.info(f"{result.name} is healthy ({result.duration_ms:.2f}ms)")
```

## Retry Configuration

Add retry logic to health checks:

```python
from healthcheckx import Health, CheckResult, HealthStatus
import time
from functools import wraps

def with_retry(max_attempts: int = 3, delay: float = 0.5):
    """Decorator to add retry logic"""
    def decorator(check_func):
        @wraps(check_func)
        def wrapper() -> CheckResult:
            last_result = None
            for attempt in range(max_attempts):
                result = check_func()
                if result.status == HealthStatus.healthy:
                    return result
                last_result = result
                if attempt < max_attempts - 1:
                    time.sleep(delay)
            return last_result
        return wrapper
    return decorator

# Usage
@with_retry(max_attempts=3, delay=0.5)
def unstable_service_check() -> CheckResult:
    # Your check logic
    pass

health = Health()
health.register(unstable_service_check)
```

## Response Format Configuration

Customize response format:

```python
from healthcheckx import Health, overall_status
from typing import Dict, Any
import json

def custom_response_format(results) -> Dict[str, Any]:
    """Custom response format"""
    status = overall_status(results)
    
    return {
        "status": status.value,
        "timestamp": "2026-01-15T10:30:00Z",
        "total_checks": len(results),
        "healthy_count": sum(1 for r in results if r.status.value == "healthy"),
        "unhealthy_count": sum(1 for r in results if r.status.value == "unhealthy"),
        "average_response_time": sum(r.duration_ms for r in results) / len(results),
        "checks": [
            {
                "name": r.name,
                "status": r.status.value,
                "duration_ms": round(r.duration_ms, 2),
                "message": r.message
            }
            for r in results
        ]
    }

health = Health()
health.redis_check("redis://localhost:6379", name="redis")
health.postgresql_check("postgresql://localhost/db", name="database")

results = health.run()
custom_response = custom_response_format(results)
print(json.dumps(custom_response, indent=2))
```

## Caching Configuration

Cache health check results to reduce load:

```python
from healthcheckx import Health
from functools import lru_cache
from datetime import datetime, timedelta
from typing import List

class CachedHealth:
    def __init__(self, health: Health, cache_duration: int = 30):
        self.health = health
        self.cache_duration = cache_duration  # seconds
        self.last_check = None
        self.cached_results = None
    
    def run(self):
        """Run checks with caching"""
        now = datetime.now()
        
        # Return cached results if still valid
        if (self.cached_results is not None and 
            self.last_check is not None and
            (now - self.last_check).total_seconds() < self.cache_duration):
            return self.cached_results
        
        # Run fresh checks
        self.cached_results = self.health.run()
        self.last_check = now
        return self.cached_results

# Usage
health = Health()
health.redis_check("redis://localhost:6379", name="redis")
health.postgresql_check("postgresql://localhost/db", name="database")

cached_health = CachedHealth(health, cache_duration=30)

# First call - runs checks
results1 = cached_health.run()

# Second call within 30 seconds - returns cached results
results2 = cached_health.run()  # Same results, no actual checks

# After 30 seconds - runs fresh checks
import time
time.sleep(31)
results3 = cached_health.run()  # New checks
```

## Framework-Specific Configuration

### FastAPI with Settings

```python
from fastapi import FastAPI
from pydantic_settings import BaseSettings
from healthcheckx import Health, FastAPIAdapter

class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    database_url: str = "postgresql://localhost/mydb"
    environment: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()

app = FastAPI()

health = Health()
health.redis_check(settings.redis_url, name="redis")
health.postgresql_check(settings.database_url, name="database")

adapter = FastAPIAdapter(health)
app.get("/health")(adapter.endpoint)
```

### Flask with Config

```python
from flask import Flask
from healthcheckx import Health, flask_health_endpoint

app = Flask(__name__)

# Load configuration
app.config.from_object('config.ProductionConfig')
# or
app.config.from_envvar('APP_CONFIG_FILE')

health = Health()
health.redis_check(app.config['REDIS_URL'], name="redis")
health.postgresql_check(app.config['DATABASE_URL'], name="database")

app.add_url_rule("/health", "health", flask_health_endpoint(health))
```

### Django with Settings

```python
# Django settings.py
HEALTH_CHECKS = {
    'REDIS_URL': 'redis://localhost:6379',
    'DATABASE_URL': 'postgresql://localhost/mydb',
    'TIMEOUT': 2,
    'ENABLE_CACHE_CHECK': True,
    'ENABLE_QUEUE_CHECK': True,
}

# health.py
from django.conf import settings
from healthcheckx import Health

def create_health():
    health = Health()
    
    config = settings.HEALTH_CHECKS
    
    health.postgresql_check(config['DATABASE_URL'], name="database")
    
    if config.get('ENABLE_CACHE_CHECK'):
        health.redis_check(config['REDIS_URL'], name="redis")
    
    return health

health = create_health()
```

## Docker Configuration

### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/mydb
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
      - HEALTH_CHECK_TIMEOUT=3
      - ENVIRONMENT=production
    depends_on:
      - postgres
      - redis
      - rabbitmq
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb
  
  redis:
    image: redis:7-alpine
  
  rabbitmq:
    image: rabbitmq:3-management-alpine
```

## Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: health-config
data:
  DATABASE_URL: "postgresql://postgres:5432/mydb"
  REDIS_URL: "redis://redis:6379"
  RABBITMQ_URL: "amqp://rabbitmq:5672"
  HEALTH_CHECK_TIMEOUT: "2"
  ENVIRONMENT: "production"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: my-app:latest
        envFrom:
        - configMapRef:
            name: health-config
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

## Best Practices

1. **Use Environment Variables** - Never hardcode credentials
2. **Set Appropriate Timeouts** - 2-3 seconds for most checks
3. **Cache When Needed** - Cache results for high-traffic endpoints
4. **Log Failures** - Always log unhealthy checks for debugging
5. **Document Configuration** - Comment why each setting exists
6. **Validate Configuration** - Check that required env vars are set
7. **Use Secrets Management** - Use proper secret management in production
8. **Test Configuration** - Test health checks in each environment
9. **Monitor Performance** - Track check duration over time
10. **Keep It Simple** - Avoid over-complicated configuration

## Configuration Checklist

- [ ] Environment variables defined
- [ ] Timeouts configured appropriately
- [ ] Logging enabled
- [ ] Secrets properly managed
- [ ] Docker health checks configured
- [ ] Kubernetes probes configured
- [ ] Error handling implemented
- [ ] Caching strategy defined
- [ ] Documentation updated
- [ ] Tests written for configuration

## Next Steps

- [Custom Health Checks](custom-checks.md) - Create custom checks
- [Multiple Instances](multiple-instances.md) - Check multiple services
- [Examples](../examples.md) - Complete configuration examples

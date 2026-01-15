# Multiple Instances

Check multiple instances of the same service type with unique names and configurations.

## Overview

In production environments, you often need to monitor multiple instances of the same service:

- Multiple Redis instances (cache, sessions, rate limiting)
- Multiple databases (primary, replica, analytics)
- Multiple message queues (orders, notifications, analytics)
- Multiple API endpoints (different regions or services)

healthcheckx makes this easy by allowing you to register multiple checks with unique names.

## Basic Example

```python
from healthcheckx import Health

health = Health()

# Multiple Redis instances
health.redis_check("redis://redis-cache:6379", name="redis-cache") \
      .redis_check("redis://redis-sessions:6379", name="redis-sessions") \
      .redis_check("redis://redis-rate-limit:6379", name="redis-rate-limit")

# Run all checks
results = health.run()

for result in results:
    print(f"{result.name}: {result.status.value}")
```

Output:
```
redis-cache: healthy
redis-sessions: healthy
redis-rate-limit: unhealthy
```

## Multiple Databases

### PostgreSQL Primary and Replicas

```python
from healthcheckx import Health

health = Health()

# Primary database
health.postgresql_check(
    "postgresql://user:pass@primary:5432/db",
    name="postgres-primary"
)

# Read replicas
health.postgresql_check(
    "postgresql://user:pass@replica1:5432/db",
    name="postgres-replica-1"
)

health.postgresql_check(
    "postgresql://user:pass@replica2:5432/db",
    name="postgres-replica-2"
)

# Analytics database
health.postgresql_check(
    "postgresql://user:pass@analytics:5432/analytics_db",
    name="postgres-analytics"
)

results = health.run()
```

### Multi-Database Setup

```python
from healthcheckx import Health

health = Health()

# Different database types
health.postgresql_check(
    "postgresql://localhost/main_db",
    name="postgres-main"
)

health.mysql_check(
    "mysql://localhost:3306/legacy_db",
    name="mysql-legacy"
)

health.mongodb_check(
    "mongodb://localhost:27017/documents",
    name="mongodb-docs"
)

health.redis_check(
    "redis://localhost:6379",
    name="redis-cache"
)

results = health.run()
```

## Environment-Based Configuration

Configure multiple instances from environment variables:

```python
from healthcheckx import Health
import os

def create_health():
    health = Health()
    
    # Primary services
    if db_url := os.getenv("DATABASE_URL"):
        health.postgresql_check(db_url, name="database-primary")
    
    if redis_url := os.getenv("REDIS_URL"):
        health.redis_check(redis_url, name="redis-main")
    
    # Optional replica
    if db_replica_url := os.getenv("DATABASE_REPLICA_URL"):
        health.postgresql_check(db_replica_url, name="database-replica")
    
    # Optional additional Redis
    if redis_session_url := os.getenv("REDIS_SESSION_URL"):
        health.redis_check(redis_session_url, name="redis-sessions")
    
    if redis_cache_url := os.getenv("REDIS_CACHE_URL"):
        health.redis_check(redis_cache_url, name="redis-cache")
    
    # Message queues
    if rabbitmq_url := os.getenv("RABBITMQ_URL"):
        health.rabbitmq_check(rabbitmq_url, name="rabbitmq-main")
    
    return health

health = create_health()
```

## Dynamic Instance Registration

Register instances dynamically from configuration:

```python
from healthcheckx import Health
from typing import List, Dict

def setup_redis_clusters(health: Health, clusters: List[Dict[str, str]]):
    """Register multiple Redis clusters"""
    for cluster in clusters:
        health.redis_check(
            cluster['url'],
            name=cluster['name']
        )

def setup_databases(health: Health, databases: List[Dict[str, str]]):
    """Register multiple databases"""
    for db in databases:
        if db['type'] == 'postgresql':
            health.postgresql_check(db['url'], name=db['name'])
        elif db['type'] == 'mysql':
            health.mysql_check(db['url'], name=db['name'])
        elif db['type'] == 'mongodb':
            health.mongodb_check(db['url'], name=db['name'])

# Configuration
redis_clusters = [
    {"name": "redis-cache-us-east", "url": "redis://cache-us-east:6379"},
    {"name": "redis-cache-eu-west", "url": "redis://cache-eu-west:6379"},
    {"name": "redis-sessions", "url": "redis://sessions:6379"},
]

databases = [
    {"name": "postgres-primary", "type": "postgresql", "url": "postgresql://primary:5432/db"},
    {"name": "postgres-replica", "type": "postgresql", "url": "postgresql://replica:5432/db"},
    {"name": "mysql-analytics", "type": "mysql", "url": "mysql://analytics:3306/analytics"},
]

# Setup health checks
health = Health()
setup_redis_clusters(health, redis_clusters)
setup_databases(health, databases)

results = health.run()
```

## Grouped Checks

Organize checks by purpose:

```python
from healthcheckx import Health
from typing import List

class HealthCheckGroups:
    def __init__(self):
        self.critical_health = Health()
        self.cache_health = Health()
        self.analytics_health = Health()
    
    def setup_critical(self):
        """Critical services that must be available"""
        self.critical_health.postgresql_check(
            "postgresql://localhost/main",
            name="database-primary"
        )
        self.critical_health.redis_check(
            "redis://localhost:6379",
            name="redis-sessions"
        )
    
    def setup_cache(self):
        """Cache services (degraded is acceptable)"""
        self.cache_health.redis_check(
            "redis://cache1:6379",
            name="cache-region-1"
        )
        self.cache_health.redis_check(
            "redis://cache2:6379",
            name="cache-region-2"
        )
        self.cache_health.memcached_check(
            "memcached://mc1:11211",
            name="memcached-1"
        )
    
    def setup_analytics(self):
        """Analytics services (optional)"""
        self.analytics_health.mongodb_check(
            "mongodb://localhost:27017/analytics",
            name="mongodb-analytics"
        )
        self.analytics_health.postgresql_check(
            "postgresql://localhost/analytics",
            name="postgres-analytics"
        )
    
    def check_critical(self):
        """Check only critical services"""
        return self.critical_health.run()
    
    def check_all(self):
        """Check all services"""
        return (
            self.critical_health.run() +
            self.cache_health.run() +
            self.analytics_health.run()
        )

# Usage
groups = HealthCheckGroups()
groups.setup_critical()
groups.setup_cache()
groups.setup_analytics()

# For Kubernetes liveness - only critical
critical_results = groups.check_critical()

# For readiness - all services
all_results = groups.check_all()
```

## Regional Deployments

Check services across multiple regions:

```python
from healthcheckx import Health
from typing import Dict, List

class RegionalHealthChecks:
    def __init__(self):
        self.regions = {}
    
    def add_region(self, region_name: str, services: Dict[str, str]):
        """Add health checks for a region"""
        health = Health()
        
        if 'redis' in services:
            health.redis_check(services['redis'], name=f"redis-{region_name}")
        
        if 'database' in services:
            health.postgresql_check(
                services['database'],
                name=f"db-{region_name}"
            )
        
        if 'cache' in services:
            health.memcached_check(
                services['cache'],
                name=f"cache-{region_name}"
            )
        
        self.regions[region_name] = health
    
    def check_region(self, region_name: str):
        """Check specific region"""
        if region_name in self.regions:
            return self.regions[region_name].run()
        return []
    
    def check_all_regions(self):
        """Check all regions"""
        all_results = []
        for region_name, health in self.regions.items():
            results = health.run()
            all_results.extend(results)
        return all_results

# Setup
regional_health = RegionalHealthChecks()

regional_health.add_region("us-east-1", {
    "redis": "redis://redis-us-east:6379",
    "database": "postgresql://db-us-east:5432/app",
    "cache": "memcached://cache-us-east:11211"
})

regional_health.add_region("eu-west-1", {
    "redis": "redis://redis-eu-west:6379",
    "database": "postgresql://db-eu-west:5432/app",
    "cache": "memcached://cache-eu-west:11211"
})

regional_health.add_region("ap-south-1", {
    "redis": "redis://redis-ap-south:6379",
    "database": "postgresql://db-ap-south:5432/app",
})

# Check all regions
all_results = regional_health.check_all_regions()

# Or check specific region
us_east_results = regional_health.check_region("us-east-1")
```

## Microservices Architecture

Check multiple backend services:

```python
from healthcheckx import Health, CheckResult, HealthStatus
import requests

def create_microservices_health():
    health = Health()
    
    # Shared infrastructure
    health.postgresql_check(
        "postgresql://localhost/users",
        name="database-users"
    )
    health.redis_check(
        "redis://localhost:6379",
        name="redis-cache"
    )
    health.rabbitmq_check(
        "amqp://localhost:5672",
        name="message-queue"
    )
    
    # Custom checks for each microservice
    def user_service_check() -> CheckResult:
        try:
            response = requests.get(
                "http://user-service:8001/health",
                timeout=2
            )
            if response.status_code == 200:
                return CheckResult("user-service", HealthStatus.healthy)
            return CheckResult(
                "user-service",
                HealthStatus.unhealthy,
                f"HTTP {response.status_code}"
            )
        except Exception as e:
            return CheckResult("user-service", HealthStatus.unhealthy, str(e))
    
    def order_service_check() -> CheckResult:
        try:
            response = requests.get(
                "http://order-service:8002/health",
                timeout=2
            )
            if response.status_code == 200:
                return CheckResult("order-service", HealthStatus.healthy)
            return CheckResult(
                "order-service",
                HealthStatus.unhealthy,
                f"HTTP {response.status_code}"
            )
        except Exception as e:
            return CheckResult("order-service", HealthStatus.unhealthy, str(e))
    
    def payment_service_check() -> CheckResult:
        try:
            response = requests.get(
                "http://payment-service:8003/health",
                timeout=2
            )
            if response.status_code == 200:
                return CheckResult("payment-service", HealthStatus.healthy)
            return CheckResult(
                "payment-service",
                HealthStatus.unhealthy,
                f"HTTP {response.status_code}"
            )
        except Exception as e:
            return CheckResult("payment-service", HealthStatus.unhealthy, str(e))
    
    health.register(user_service_check)
    health.register(order_service_check)
    health.register(payment_service_check)
    
    return health

health = create_microservices_health()
```

## Filtering Results

Filter results by status or name:

```python
from healthcheckx import Health, HealthStatus

health = Health()

# Register multiple checks
health.redis_check("redis://cache1:6379", name="redis-cache-1") \
      .redis_check("redis://cache2:6379", name="redis-cache-2") \
      .postgresql_check("postgresql://localhost/db", name="postgres") \
      .mongodb_check("mongodb://localhost:27017", name="mongodb")

results = health.run()

# Filter unhealthy services
unhealthy = [r for r in results if r.status == HealthStatus.unhealthy]
print(f"Unhealthy services: {[r.name for r in unhealthy]}")

# Filter by name pattern
redis_results = [r for r in results if 'redis' in r.name]
print(f"Redis checks: {[r.name for r in redis_results]}")

# Get specific check result
postgres_result = next((r for r in results if r.name == "postgres"), None)
if postgres_result:
    print(f"PostgreSQL: {postgres_result.status.value}")
```

## Parallel vs Sequential Execution

All checks run in parallel by default for better performance:

```python
from healthcheckx import Health
import time

health = Health()

# These all run in parallel (fast)
health.redis_check("redis://redis1:6379", name="redis-1") \
      .redis_check("redis://redis2:6379", name="redis-2") \
      .redis_check("redis://redis3:6379", name="redis-3") \
      .postgresql_check("postgresql://db1:5432/db", name="postgres-1") \
      .postgresql_check("postgresql://db2:5432/db", name="postgres-2")

start = time.time()
results = health.run()
duration = time.time() - start

print(f"Checked {len(results)} services in {duration:.2f}s")
# Output: Checked 5 services in 0.15s (not 0.75s if sequential)
```

## Conditional Registration

Register checks based on environment:

```python
from healthcheckx import Health
import os

def create_health_checks():
    health = Health()
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Always check primary database
    health.postgresql_check(
        os.getenv("DATABASE_URL"),
        name="database-primary"
    )
    
    # Production: check replicas
    if environment == "production":
        if replica_url := os.getenv("DATABASE_REPLICA_URL"):
            health.postgresql_check(replica_url, name="database-replica")
        
        # Check multiple Redis instances
        health.redis_check(
            os.getenv("REDIS_CACHE_URL"),
            name="redis-cache"
        )
        health.redis_check(
            os.getenv("REDIS_SESSION_URL"),
            name="redis-sessions"
        )
    
    # Development: single Redis
    else:
        health.redis_check(
            os.getenv("REDIS_URL", "redis://localhost:6379"),
            name="redis"
        )
    
    # Staging and Production: check message queue
    if environment in ["staging", "production"]:
        if rabbitmq_url := os.getenv("RABBITMQ_URL"):
            health.rabbitmq_check(rabbitmq_url, name="message-queue")
    
    return health

health = create_health_checks()
```

## Response Organization

Organize multiple check results:

```python
from healthcheckx import Health, overall_status, HealthStatus
from typing import Dict, List

health = Health()

# Register many checks
health.redis_check("redis://cache:6379", name="redis-cache") \
      .redis_check("redis://sessions:6379", name="redis-sessions") \
      .postgresql_check("postgresql://primary:5432/db", name="postgres-primary") \
      .postgresql_check("postgresql://replica:5432/db", name="postgres-replica") \
      .mongodb_check("mongodb://localhost:27017", name="mongodb")

results = health.run()

# Organize by service type
organized = {
    "redis": [],
    "postgresql": [],
    "mongodb": []
}

for result in results:
    if "redis" in result.name:
        organized["redis"].append(result)
    elif "postgres" in result.name:
        organized["postgresql"].append(result)
    elif "mongodb" in result.name:
        organized["mongodb"].append(result)

# Create summary
summary = {
    "status": overall_status(results).value,
    "services": {
        service_type: {
            "total": len(checks),
            "healthy": sum(1 for c in checks if c.status == HealthStatus.healthy),
            "unhealthy": sum(1 for c in checks if c.status == HealthStatus.unhealthy),
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "duration_ms": c.duration_ms
                }
                for c in checks
            ]
        }
        for service_type, checks in organized.items()
    }
}

print(summary)
```

## Best Practices

1. **Use Descriptive Names** - Make names clear and unique: `redis-cache-us-east` not `redis1`
2. **Group by Purpose** - Separate critical, optional, and analytics checks
3. **Environment-Based** - Register different checks for dev/staging/prod
4. **Consistent Naming** - Use patterns like `{service}-{purpose}-{region}`
5. **Filter Results** - Process results by service type or status
6. **Monitor Performance** - Track check duration for multiple instances
7. **Fail Gracefully** - One failing instance shouldn't crash all checks
8. **Document Dependencies** - Comment why each instance is needed

## Common Patterns

### Pattern 1: Primary + Replicas

```python
health = Health()
health.postgresql_check(primary_url, name="db-primary")
health.postgresql_check(replica_url, name="db-replica")
```

### Pattern 2: Multi-Region

```python
for region in ["us-east", "eu-west", "ap-south"]:
    health.redis_check(f"redis://{region}:6379", name=f"redis-{region}")
```

### Pattern 3: Service Mesh

```python
for service in ["auth", "orders", "payments", "notifications"]:
    health.register(create_service_check(service))
```

### Pattern 4: Sharded Databases

```python
for shard_id in range(1, 5):
    health.postgresql_check(
        f"postgresql://shard{shard_id}:5432/db",
        name=f"postgres-shard-{shard_id}"
    )
```

## Next Steps

- [Custom Health Checks](custom-checks.md) - Create custom checks
- [Configuration](configuration.md) - Configure timeouts and behavior
- [Examples](../examples.md) - Complete working examples

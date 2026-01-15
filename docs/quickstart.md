# Quick Start

Get up and running with healthcheckx in minutes!

## Your First Health Check

### Step 1: Install healthcheckx

```bash
pip install healthcheckx[redis,postgresql]
```

### Step 2: Create a Health Check

```python
from healthcheckx import Health

# Create health check instance
health = Health()

# Register checks
health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://user:password@localhost/mydb")

# Run all checks
results = health.run()

# Print results
for result in results:
    print(f"{result.name}: {result.status}")
```

**Output:**
```
redis: healthy
postgresql: healthy
```

## Detailed Results

Each health check returns detailed information:

```python
from healthcheckx import Health

health = Health()
health.redis_check("redis://localhost:6379")

results = health.run()

for result in results:
    print(f"Name: {result.name}")
    print(f"Status: {result.status}")
    print(f"Duration: {result.duration_ms:.2f}ms")
    if result.message:
        print(f"Message: {result.message}")
```

## Overall Status

Get an aggregate status across all checks:

```python
from healthcheckx import Health, overall_status

health = Health()
health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://user:pass@localhost/db") \
      .mongodb_check("mongodb://localhost:27017")

results = health.run()
status = overall_status(results)

print(f"Overall Status: {status}")
# Output: Overall Status: healthy
```

## Multiple Service Instances

Monitor multiple instances of the same service using the `name` parameter:

```python
from healthcheckx import Health

health = Health()

# Monitor multiple Redis instances
health.redis_check("redis://primary:6379", name="redis-primary") \
      .redis_check("redis://cache:6379", name="redis-cache") \
      .redis_check("redis://sessions:6379", name="redis-sessions")

results = health.run()

for result in results:
    print(f"{result.name}: {result.status}")
```

**Output:**
```
redis-primary: healthy
redis-cache: healthy
redis-sessions: healthy
```

## Handling Unhealthy Services

healthcheckx gracefully handles failures:

```python
from healthcheckx import Health, HealthStatus

health = Health()
health.redis_check("redis://nonexistent:6379")

results = health.run()

for result in results:
    if result.status == HealthStatus.unhealthy:
        print(f"⚠️ {result.name} is unhealthy")
        print(f"Error: {result.message}")
```

## Custom Timeouts

Configure timeouts for each check:

```python
from healthcheckx import Health

health = Health()

# Fast timeout for cache
health.redis_check("redis://localhost:6379", timeout=1)

# Longer timeout for database
health.postgresql_check("postgresql://localhost/db", timeout=5)

# Medium timeout for MongoDB
health.mongodb_check("mongodb://localhost:27017", timeout=3)

results = health.run()
```

## Framework Integration

### FastAPI Example

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

# Start server
# uvicorn main:app --reload
```

Visit `http://localhost:8000/health` to see health status.

### Flask Example

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

if __name__ == "__main__":
    app.run(debug=True)
```

## Custom Health Checks

Create your own health checks:

```python
from healthcheckx import Health, CheckResult, HealthStatus

def disk_space_check():
    """Check if disk space is available"""
    import shutil
    stat = shutil.disk_usage("/")
    free_percent = (stat.free / stat.total) * 100
    
    if free_percent > 20:
        return CheckResult("disk-space", HealthStatus.healthy)
    elif free_percent > 10:
        return CheckResult("disk-space", HealthStatus.degraded, 
                          f"Low disk space: {free_percent:.1f}%")
    else:
        return CheckResult("disk-space", HealthStatus.unhealthy,
                          f"Critical disk space: {free_percent:.1f}%")

health = Health()
health.register(disk_space_check)
health.redis_check("redis://localhost:6379")

results = health.run()
```

## Common Patterns

### Environment-Based Configuration

```python
import os
from healthcheckx import Health

health = Health()

# Load from environment variables
if redis_url := os.getenv("REDIS_URL"):
    health.redis_check(redis_url)

if db_url := os.getenv("DATABASE_URL"):
    health.postgresql_check(db_url)

if mongodb_url := os.getenv("MONGODB_URL"):
    health.mongodb_check(mongodb_url)

results = health.run()
```

### Error Handling

```python
from healthcheckx import Health, HealthStatus
import logging

health = Health()
health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://localhost/db")

results = health.run()

for result in results:
    if result.status == HealthStatus.unhealthy:
        logging.error(f"{result.name} is unhealthy: {result.message}")
    elif result.status == HealthStatus.degraded:
        logging.warning(f"{result.name} is degraded: {result.message}")
    else:
        logging.info(f"{result.name} is healthy")
```

## Next Steps

- [Built-in Checks](checks/cache.md) - Explore all available health checks
- [Framework Integration](frameworks/fastapi.md) - Deep dive into framework adapters
- [Custom Checks](advanced/custom-checks.md) - Learn to create advanced custom checks
- [API Reference](api-reference.md) - Complete API documentation

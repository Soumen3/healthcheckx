# FastAPI Integration

Integrate healthcheckx with FastAPI applications for modern async health check endpoints.

## Installation

```bash
pip install fastapi uvicorn healthcheckx[all]
```

## Basic Integration

### Simple Example

```python
from fastapi import FastAPI
from healthcheckx import Health, FastAPIAdapter

app = FastAPI()
health = Health()

# Register health checks
health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://user:pass@localhost/db")

# Create adapter and add endpoint
adapter = FastAPIAdapter(health)
app.get("/health")(adapter.endpoint)

# Run with: uvicorn main:app --reload
```

Visit `http://localhost:8000/health` to see the health status.

## Response Format

### Healthy Response (HTTP 200)

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

### Unhealthy Response (HTTP 503)

```json
{
  "status": "unhealthy",
  "checks": [
    {
      "name": "redis",
      "status": "unhealthy",
      "message": "Connection refused",
      "duration_ms": 2001.2
    },
    {
      "name": "postgresql",
      "status": "healthy",
      "duration_ms": 38.7
    }
  ]
}
```

## Complete Example

```python
from fastapi import FastAPI, Response
from healthcheckx import Health, FastAPIAdapter
import os

app = FastAPI(
    title="My API",
    description="API with health checks",
    version="1.0.0"
)

# Initialize health checks
health = Health()

# Register checks from environment
if redis_url := os.getenv("REDIS_URL"):
    health.redis_check(redis_url, name="redis-cache")

if db_url := os.getenv("DATABASE_URL"):
    health.postgresql_check(db_url, name="postgres-main")

if mongodb_url := os.getenv("MONGODB_URL"):
    health.mongodb_check(mongodb_url, name="mongo-data")

# Create adapter
adapter = FastAPIAdapter(health)

# Add health endpoint
@app.get(
    "/health",
    tags=["monitoring"],
    summary="Health Check",
    description="Check the health of all services"
)
async def health_check():
    return await adapter.endpoint()

# Optional: Separate liveness endpoint
@app.get(
    "/healthz",
    tags=["monitoring"],
    summary="Liveness Probe",
    description="Check if the application is alive"
)
async def liveness():
    return {"status": "ok"}

# Optional: Separate readiness endpoint
@app.get(
    "/ready",
    tags=["monitoring"],
    summary="Readiness Probe",
    description="Check if the application is ready to serve traffic"
)
async def readiness():
    return await adapter.endpoint()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Multiple Endpoints

Create different health check endpoints for different purposes:

```python
from fastapi import FastAPI
from healthcheckx import Health, FastAPIAdapter

app = FastAPI()

# Critical services (for liveness)
critical_health = Health()
critical_health.postgresql_check("postgresql://localhost/db", name="database")

# All services (for readiness)
full_health = Health()
full_health.postgresql_check("postgresql://localhost/db", name="database") \
           .redis_check("redis://localhost:6379", name="cache") \
           .rabbitmq_check("amqp://guest:guest@localhost:5672", name="queue")

# Separate adapters
critical_adapter = FastAPIAdapter(critical_health)
full_adapter = FastAPIAdapter(full_health)

# Liveness - only checks critical services
@app.get("/healthz")
async def liveness():
    return await critical_adapter.endpoint()

# Readiness - checks all services
@app.get("/ready")
async def readiness():
    return await full_adapter.endpoint()
```

## Kubernetes Integration

### With Probes

```python
from fastapi import FastAPI
from healthcheckx import Health, FastAPIAdapter

app = FastAPI()
health = Health()

health.postgresql_check("postgresql://postgres:5432/db") \
      .redis_check("redis://redis:6379")

adapter = FastAPIAdapter(health)

# Liveness probe - is the app alive?
@app.get("/healthz")
async def liveness():
    return {"status": "ok"}

# Readiness probe - is the app ready to serve traffic?
@app.get("/ready")
async def readiness():
    return await adapter.endpoint()

# Startup probe - has the app finished starting?
@app.get("/startup")
async def startup():
    return await adapter.endpoint()
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: my-api:latest
        ports:
        - containerPort: 8000
        
        # Liveness probe - restart if fails
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        # Readiness probe - remove from service if fails
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        # Startup probe - wait for app to start
        startupProbe:
          httpGet:
            path: /startup
            port: 8000
          initialDelaySeconds: 0
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 30
```

## Custom Response Format

Customize the response format:

```python
from fastapi import FastAPI, Response
from healthcheckx import Health, overall_status
from typing import Dict, Any
import json

app = FastAPI()
health = Health()

health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://localhost/db")

@app.get("/health")
async def health_check():
    results = health.run()
    status = overall_status(results)
    
    # Custom response format
    response_data = {
        "application": "my-api",
        "version": "1.0.0",
        "status": status.value,
        "timestamp": "2026-01-15T10:30:00Z",
        "services": [
            {
                "name": r.name,
                "healthy": r.status == "healthy",
                "responseTime": f"{r.duration_ms:.2f}ms",
                "error": r.message if r.message else None
            }
            for r in results
        ]
    }
    
    status_code = 200 if status != "unhealthy" else 503
    return Response(
        content=json.dumps(response_data, indent=2),
        status_code=status_code,
        media_type="application/json"
    )
```

## Async Custom Checks

Create async custom health checks:

```python
from fastapi import FastAPI
from healthcheckx import Health, CheckResult, HealthStatus, FastAPIAdapter
import httpx

app = FastAPI()
health = Health()

# Regular sync checks
health.redis_check("redis://localhost:6379")

# Async custom check
async def external_api_check() -> CheckResult:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.example.com/status",
                timeout=2.0
            )
            if response.status_code == 200:
                return CheckResult("external-api", HealthStatus.healthy)
            else:
                return CheckResult(
                    "external-api",
                    HealthStatus.unhealthy,
                    f"HTTP {response.status_code}"
                )
    except Exception as e:
        return CheckResult("external-api", HealthStatus.unhealthy, str(e))

# Wrapper to make it sync for healthcheckx
def external_api_check_sync() -> CheckResult:
    import asyncio
    return asyncio.run(external_api_check())

health.register(external_api_check_sync)

adapter = FastAPIAdapter(health)
app.get("/health")(adapter.endpoint)
```

## Middleware Integration

Add health check middleware:

```python
from fastapi import FastAPI, Request
from healthcheckx import Health, FastAPIAdapter
import time

app = FastAPI()
health = Health()

health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://localhost/db")

adapter = FastAPIAdapter(health)

# Add health endpoint
@app.get("/health")
async def health_check():
    return await adapter.endpoint()

# Middleware to log health check requests
@app.middleware("http")
async def log_health_checks(request: Request, call_next):
    if request.url.path == "/health":
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        print(f"Health check: {response.status_code} in {duration:.3f}s")
        return response
    return await call_next(request)
```

## OpenAPI/Swagger Documentation

The health endpoint will automatically appear in FastAPI's interactive docs:

```python
from fastapi import FastAPI
from healthcheckx import Health, FastAPIAdapter

app = FastAPI(
    title="My API",
    description="API with comprehensive health checks"
)

health = Health()
health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://localhost/db")

adapter = FastAPIAdapter(health)

@app.get(
    "/health",
    tags=["monitoring"],
    summary="Health Check Endpoint",
    description="Returns the health status of all services",
    responses={
        200: {
            "description": "All services are healthy or degraded",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "checks": [
                            {
                                "name": "redis",
                                "status": "healthy",
                                "duration_ms": 12.5
                            }
                        ]
                    }
                }
            }
        },
        503: {
            "description": "One or more services are unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "checks": [
                            {
                                "name": "redis",
                                "status": "unhealthy",
                                "message": "Connection refused",
                                "duration_ms": 2001.2
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def health_check():
    return await adapter.endpoint()
```

Visit `http://localhost:8000/docs` to see the interactive documentation.

## Docker Integration

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health').raise_for_status()"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/mydb
    depends_on:
      - redis
      - postgres
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"
```

## Best Practices

1. **Separate Liveness and Readiness** - Use different endpoints for Kubernetes probes
2. **Set Appropriate Timeouts** - Keep health checks fast (< 3 seconds total)
3. **Cache Results** - For high-traffic apps, cache health check results for a few seconds
4. **Monitor Dependencies Only** - Don't include business logic in health checks
5. **Use Async When Possible** - FastAPI's async nature works well with health checks
6. **Document in OpenAPI** - Add proper descriptions and examples for Swagger docs

## Troubleshooting

### Health Endpoint Returns 404

Make sure you're using the correct decorator:

```python
# ✅ Correct
adapter = FastAPIAdapter(health)
app.get("/health")(adapter.endpoint)

# ❌ Wrong
app.get("/health")(health.run)
```

### Async Warning

If you see async warnings, ensure you're calling the adapter correctly:

```python
# ✅ Correct
@app.get("/health")
async def health_check():
    return await adapter.endpoint()

# ✅ Also correct (FastAPI handles it)
app.get("/health")(adapter.endpoint)
```

## Next Steps

- [Flask Integration](flask.md) - Flask framework integration
- [Django Integration](django.md) - Django framework integration
- [Custom Checks](../advanced/custom-checks.md) - Create custom health checks

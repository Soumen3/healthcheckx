# Examples

Complete, working examples demonstrating healthcheckx in various scenarios.

## Quick Start Example

The simplest possible health check:

```python
from healthcheckx import Health

# Create health check instance
health = Health()

# Add checks
health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://localhost/mydb")

# Run checks
results = health.run()

# Print results
for result in results:
    print(f"{result.name}: {result.status.value}")
```

## Web Application Examples

### FastAPI Application

Complete FastAPI application with health checks:

```python
from fastapi import FastAPI
from healthcheckx import Health, FastAPIAdapter
import os

app = FastAPI(title="My API", version="1.0.0")

# Initialize health checks
health = Health()

# Register checks from environment
health.postgresql_check(
    os.getenv("DATABASE_URL", "postgresql://localhost/mydb"),
    name="database"
)

health.redis_check(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    name="cache"
)

health.rabbitmq_check(
    os.getenv("RABBITMQ_URL", "amqp://localhost:5672"),
    name="message-queue"
)

# Create adapter and add endpoint
adapter = FastAPIAdapter(health)

@app.get("/health", tags=["monitoring"])
async def health_check():
    """Health check endpoint for all services"""
    return await adapter.endpoint()

@app.get("/healthz", tags=["monitoring"])
async def liveness():
    """Liveness probe - always returns OK"""
    return {"status": "ok"}

@app.get("/ready", tags=["monitoring"])
async def readiness():
    """Readiness probe - checks all dependencies"""
    return await adapter.endpoint()

# Application endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome to My API"}

@app.get("/api/items")
def get_items():
    # Your business logic
    return {"items": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Run with:
```bash
uvicorn main:app --reload
```

### Flask Application

Complete Flask application with health checks:

```python
from flask import Flask, jsonify
from healthcheckx import Health, flask_health_endpoint
import os

app = Flask(__name__)

# Initialize health checks
health = Health()

health.postgresql_check(
    os.getenv("DATABASE_URL", "postgresql://localhost/mydb"),
    name="database"
)

health.redis_check(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    name="cache"
)

# Add health endpoint
app.add_url_rule("/health", "health", flask_health_endpoint(health))

@app.route("/healthz")
def liveness():
    """Liveness probe"""
    return jsonify({"status": "ok"}), 200

@app.route("/ready")
def readiness():
    """Readiness probe"""
    return flask_health_endpoint(health)()

# Application routes
@app.route("/")
def index():
    return jsonify({"message": "Welcome to My API"})

@app.route("/api/users")
def get_users():
    # Your business logic
    return jsonify({"users": []})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

Run with:
```bash
python app.py
```

### Django Application

Complete Django setup with health checks:

**myproject/api/health.py:**
```python
from healthcheckx import Health
from django.conf import settings
import os

def create_health():
    health = Health()
    
    # Database from Django settings
    db_config = settings.DATABASES['default']
    if db_config['ENGINE'] == 'django.db.backends.postgresql':
        db_url = (
            f"postgresql://{db_config['USER']}:{db_config['PASSWORD']}"
            f"@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
        )
        health.postgresql_check(db_url, name="database")
    
    # Cache from Django settings
    cache_config = settings.CACHES['default']
    if 'redis' in cache_config['BACKEND'].lower():
        health.redis_check(cache_config['LOCATION'], name="cache")
    
    # Additional services from environment
    if rabbitmq_url := os.getenv("RABBITMQ_URL"):
        health.rabbitmq_check(rabbitmq_url, name="message-queue")
    
    return health

health = create_health()
```

**myproject/api/views.py:**
```python
from django.http import JsonResponse
from healthcheckx import django_health_view
from .health import health

# Health check views
health_check = django_health_view(health)

def liveness(request):
    return JsonResponse({"status": "ok"})

readiness = django_health_view(health)
```

**myproject/api/urls.py:**
```python
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('healthz/', views.liveness, name='liveness'),
    path('ready/', views.readiness, name='readiness'),
]
```

**myproject/urls.py:**
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
]
```

## Microservices Example

Health checks for a microservices architecture:

```python
from healthcheckx import Health, CheckResult, HealthStatus
import requests
import os

def create_microservices_health():
    health = Health()
    
    # Shared infrastructure
    health.postgresql_check(
        os.getenv("DATABASE_URL"),
        name="postgres-shared"
    )
    
    health.redis_check(
        os.getenv("REDIS_URL"),
        name="redis-cache"
    )
    
    health.rabbitmq_check(
        os.getenv("RABBITMQ_URL"),
        name="message-queue"
    )
    
    # Microservice health checks
    services = [
        ("user-service", "http://user-service:8001/health"),
        ("order-service", "http://order-service:8002/health"),
        ("payment-service", "http://payment-service:8003/health"),
        ("notification-service", "http://notification-service:8004/health"),
    ]
    
    for service_name, service_url in services:
        def create_service_check(name, url):
            def check() -> CheckResult:
                try:
                    response = requests.get(url, timeout=2)
                    if response.status_code == 200:
                        return CheckResult(name, HealthStatus.healthy)
                    return CheckResult(
                        name,
                        HealthStatus.unhealthy,
                        f"HTTP {response.status_code}"
                    )
                except Exception as e:
                    return CheckResult(name, HealthStatus.unhealthy, str(e))
            return check
        
        health.register(create_service_check(service_name, service_url))
    
    return health

# Use in your API gateway or service mesh
health = create_microservices_health()
```

## Multiple Environments Example

Different configurations for different environments:

```python
from healthcheckx import Health
import os

def create_health_for_environment():
    health = Health()
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "development":
        # Development: local services
        health.redis_check("redis://localhost:6379", name="redis")
        health.postgresql_check("postgresql://localhost/mydb_dev", name="database")
    
    elif environment == "staging":
        # Staging: cloud services with replicas
        health.postgresql_check(
            os.getenv("DATABASE_URL"),
            name="postgres-primary"
        )
        health.postgresql_check(
            os.getenv("DATABASE_REPLICA_URL"),
            name="postgres-replica"
        )
        health.redis_check(os.getenv("REDIS_URL"), name="redis-cache")
        health.rabbitmq_check(os.getenv("RABBITMQ_URL"), name="rabbitmq")
    
    elif environment == "production":
        # Production: full monitoring
        health.postgresql_check(
            os.getenv("DATABASE_URL"),
            name="postgres-primary"
        )
        health.postgresql_check(
            os.getenv("DATABASE_REPLICA_URL"),
            name="postgres-replica"
        )
        health.redis_check(
            os.getenv("REDIS_CACHE_URL"),
            name="redis-cache"
        )
        health.redis_check(
            os.getenv("REDIS_SESSION_URL"),
            name="redis-sessions"
        )
        health.rabbitmq_check(os.getenv("RABBITMQ_URL"), name="rabbitmq")
        health.mongodb_check(os.getenv("MONGODB_URL"), name="mongodb")
    
    return health

health = create_health_for_environment()
```

## Custom Health Check Example

Custom health check for external API:

```python
from healthcheckx import Health, CheckResult, HealthStatus
import requests

health = Health()

# Built-in checks
health.redis_check("redis://localhost:6379", name="redis")
health.postgresql_check("postgresql://localhost/mydb", name="database")

# Custom external API check
def payment_gateway_check() -> CheckResult:
    """Check payment gateway availability"""
    try:
        response = requests.get(
            "https://api.stripe.com/v1/charges",
            headers={
                "Authorization": f"Bearer {os.getenv('STRIPE_SECRET_KEY')}"
            },
            timeout=3
        )
        
        if response.status_code in [200, 401]:  # 401 means API is up
            return CheckResult("payment-gateway", HealthStatus.healthy)
        else:
            return CheckResult(
                "payment-gateway",
                HealthStatus.unhealthy,
                f"HTTP {response.status_code}"
            )
    except requests.Timeout:
        return CheckResult(
            "payment-gateway",
            HealthStatus.unhealthy,
            "Request timeout"
        )
    except Exception as e:
        return CheckResult("payment-gateway", HealthStatus.unhealthy, str(e))

# Custom disk space check
def disk_space_check() -> CheckResult:
    """Check available disk space"""
    import shutil
    
    try:
        total, used, free = shutil.disk_usage("/")
        percent_used = (used / total) * 100
        
        if percent_used > 90:
            return CheckResult(
                "disk-space",
                HealthStatus.unhealthy,
                f"Disk usage critical: {percent_used:.1f}%"
            )
        elif percent_used > 75:
            return CheckResult(
                "disk-space",
                HealthStatus.degraded,
                f"Disk usage high: {percent_used:.1f}%"
            )
        else:
            return CheckResult("disk-space", HealthStatus.healthy)
    except Exception as e:
        return CheckResult("disk-space", HealthStatus.unhealthy, str(e))

# Register custom checks
health.register(payment_gateway_check)
health.register(disk_space_check)

# Run all checks
results = health.run()
```

## Docker Compose Example

Complete docker-compose setup with health checks:

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/mydb
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
      - ENVIRONMENT=production
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

**app.py:**
```python
from fastapi import FastAPI
from healthcheckx import Health, FastAPIAdapter
import os

app = FastAPI()

health = Health()
health.postgresql_check(os.getenv("DATABASE_URL"), name="postgres")
health.redis_check(os.getenv("REDIS_URL"), name="redis")
health.rabbitmq_check(os.getenv("RABBITMQ_URL"), name="rabbitmq")

adapter = FastAPIAdapter(health)
app.get("/health")(adapter.endpoint)

@app.get("/")
def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Kubernetes Example

Complete Kubernetes deployment with health checks:

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: app
        image: my-app:1.0.0
        ports:
        - containerPort: 8000
          name: http
        
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: RABBITMQ_URL
          value: "amqp://rabbitmq-service:5672"
        - name: ENVIRONMENT
          value: "production"
        
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        
        # Liveness probe - restart if unhealthy
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        # Readiness probe - don't send traffic if not ready
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        # Startup probe - give time to start
        startupProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 0
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 30

---
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  selector:
    app: my-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  database-url: "postgresql://user:pass@postgres-service:5432/mydb"
```

## Multi-Database Example

Application using multiple databases:

```python
from healthcheckx import Health
import os

health = Health()

# PostgreSQL - Main application database
health.postgresql_check(
    os.getenv("POSTGRES_URL", "postgresql://localhost/app_db"),
    name="postgres-main"
)

# MySQL - Legacy system integration
health.mysql_check(
    os.getenv("MYSQL_URL", "mysql://localhost:3306/legacy_db"),
    name="mysql-legacy"
)

# MongoDB - Document storage
health.mongodb_check(
    os.getenv("MONGODB_URL", "mongodb://localhost:27017/documents"),
    name="mongodb-docs"
)

# SQLite - Local cache database
health.sqlite_check(
    os.getenv("SQLITE_PATH", "sqlite:///cache.db"),
    name="sqlite-cache"
)

# Redis - Session storage
health.redis_check(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    name="redis-sessions"
)

# Run checks
results = health.run()

# Categorize results
db_results = [r for r in results if any(db in r.name for db in ['postgres', 'mysql', 'mongodb', 'sqlite'])]
cache_results = [r for r in results if 'redis' in r.name]

print("Database Health:")
for result in db_results:
    print(f"  {result.name}: {result.status.value}")

print("\nCache Health:")
for result in cache_results:
    print(f"  {result.name}: {result.status.value}")
```

## Regional Deployment Example

Multi-region deployment with health monitoring:

```python
from healthcheckx import Health
from typing import Dict
import os

class RegionalHealth:
    def __init__(self):
        self.regions = {}
    
    def add_region(self, region_name: str):
        health = Health()
        
        # Database for this region
        health.postgresql_check(
            os.getenv(f"{region_name.upper()}_DATABASE_URL"),
            name=f"postgres-{region_name}"
        )
        
        # Cache for this region
        health.redis_check(
            os.getenv(f"{region_name.upper()}_REDIS_URL"),
            name=f"redis-{region_name}"
        )
        
        self.regions[region_name] = health
    
    def check_all_regions(self):
        all_results = {}
        for region, health in self.regions.items():
            all_results[region] = health.run()
        return all_results

# Setup regions
regional = RegionalHealth()
regional.add_region("us-east-1")
regional.add_region("eu-west-1")
regional.add_region("ap-south-1")

# Check all regions
results = regional.check_all_regions()

for region, checks in results.items():
    print(f"\n{region}:")
    for check in checks:
        print(f"  {check.name}: {check.status.value}")
```

## CLI Tool Example

Command-line health check tool:

```python
#!/usr/bin/env python3
"""Health check CLI tool"""

import argparse
import sys
from healthcheckx import Health, HealthStatus
import os

def main():
    parser = argparse.ArgumentParser(description='Run health checks')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    # Setup health checks
    health = Health()
    
    if db_url := os.getenv("DATABASE_URL"):
        health.postgresql_check(db_url, name="database")
    
    if redis_url := os.getenv("REDIS_URL"):
        health.redis_check(redis_url, name="redis")
    
    if rabbitmq_url := os.getenv("RABBITMQ_URL"):
        health.rabbitmq_check(rabbitmq_url, name="rabbitmq")
    
    # Run checks
    results = health.run()
    
    # Output results
    if args.json:
        import json
        output = {
            "status": "healthy" if all(r.status == HealthStatus.healthy for r in results) else "unhealthy",
            "checks": [
                {
                    "name": r.name,
                    "status": r.status.value,
                    "duration_ms": r.duration_ms,
                    "message": r.message
                }
                for r in results
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        print("Health Check Results:")
        print("-" * 50)
        for result in results:
            status_symbol = "✓" if result.status == HealthStatus.healthy else "✗"
            print(f"{status_symbol} {result.name}: {result.status.value}")
            if args.verbose and result.message:
                print(f"  Message: {result.message}")
            if args.verbose:
                print(f"  Duration: {result.duration_ms:.2f}ms")
        print("-" * 50)
    
    # Exit with error if any check failed
    if any(r.status == HealthStatus.unhealthy for r in results):
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
```

Usage:
```bash
# Basic check
python healthcheck.py

# JSON output
python healthcheck.py --json

# Verbose output
python healthcheck.py --verbose
```

## Testing Example

Unit tests for health checks:

```python
import unittest
from unittest.mock import patch, MagicMock
from healthcheckx import Health, HealthStatus

class TestHealthChecks(unittest.TestCase):
    
    def test_redis_healthy(self):
        """Test Redis health check returns healthy when connected"""
        health = Health()
        health.redis_check("redis://localhost:6379", name="redis")
        
        with patch('redis.Redis') as mock_redis:
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            mock_redis.from_url.return_value = mock_instance
            
            results = health.run()
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].status, HealthStatus.healthy)
    
    def test_postgres_unhealthy(self):
        """Test PostgreSQL check returns unhealthy when connection fails"""
        health = Health()
        health.postgresql_check("postgresql://localhost/test", name="postgres")
        
        with patch('psycopg2.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection refused")
            
            results = health.run()
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].status, HealthStatus.unhealthy)
    
    def test_multiple_checks(self):
        """Test multiple health checks"""
        health = Health()
        health.redis_check("redis://localhost:6379", name="redis")
        health.postgresql_check("postgresql://localhost/test", name="postgres")
        
        results = health.run()
        self.assertEqual(len(results), 2)
        self.assertIn("redis", [r.name for r in results])
        self.assertIn("postgres", [r.name for r in results])

if __name__ == '__main__':
    unittest.main()
```

## Next Steps

- [Installation](installation.md) - Install healthcheckx
- [Quick Start](quickstart.md) - Get started quickly
- [Built-in Checks](checks/cache.md) - Explore available checks
- [Framework Integration](frameworks/fastapi.md) - Integrate with your framework
- [API Reference](api-reference.md) - Complete API documentation

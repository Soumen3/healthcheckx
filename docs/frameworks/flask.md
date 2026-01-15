# Flask Integration

Integrate healthcheckx with Flask applications for simple and effective health check endpoints.

## Installation

```bash
pip install flask healthcheckx[all]
```

## Basic Integration

### Simple Example

```python
from flask import Flask
from healthcheckx import Health, flask_health_endpoint

app = Flask(__name__)
health = Health()

# Register health checks
health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://user:pass@localhost/db")

# Add health endpoint
app.add_url_rule("/health", "health", flask_health_endpoint(health))

if __name__ == "__main__":
    app.run(debug=True)
```

Visit `http://localhost:5000/health` to see the health status.

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
from flask import Flask, jsonify
from healthcheckx import Health, flask_health_endpoint
import os

app = Flask(__name__)

# Initialize health checks
health = Health()

# Register checks from environment
if redis_url := os.getenv("REDIS_URL"):
    health.redis_check(redis_url, name="redis-cache")

if db_url := os.getenv("DATABASE_URL"):
    health.postgresql_check(db_url, name="postgres-main")

if mongodb_url := os.getenv("MONGODB_URL"):
    health.mongodb_check(mongodb_url, name="mongo-data")

if rabbitmq_url := os.getenv("RABBITMQ_URL"):
    health.rabbitmq_check(rabbitmq_url, name="message-queue")

# Add health endpoint
app.add_url_rule("/health", "health", flask_health_endpoint(health))

# Optional: Liveness endpoint (simple alive check)
@app.route("/healthz")
def liveness():
    return jsonify({"status": "ok"}), 200

# Optional: Separate readiness endpoint
@app.route("/ready")
def readiness():
    return flask_health_endpoint(health)()

# Main application endpoints
@app.route("/")
def index():
    return jsonify({"message": "Welcome to the API"})

@app.route("/api/data")
def get_data():
    # Your business logic here
    return jsonify({"data": []})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

## Blueprint Integration

Organize health checks in a blueprint:

```python
from flask import Flask, Blueprint
from healthcheckx import Health, flask_health_endpoint

# Create monitoring blueprint
monitoring = Blueprint('monitoring', __name__, url_prefix='/monitoring')

# Create health checks
health = Health()
health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://localhost/db")

# Add health endpoint to blueprint
monitoring.add_url_rule("/health", "health", flask_health_endpoint(health))

@monitoring.route("/ping")
def ping():
    return {"status": "pong"}, 200

# Create app and register blueprint
app = Flask(__name__)
app.register_blueprint(monitoring)

if __name__ == "__main__":
    app.run(debug=True)
```

Access health check at: `http://localhost:5000/monitoring/health`

## Multiple Health Check Endpoints

Create different health check configurations:

```python
from flask import Flask
from healthcheckx import Health, flask_health_endpoint

app = Flask(__name__)

# Critical services only (for liveness probe)
critical_health = Health()
critical_health.postgresql_check("postgresql://localhost/db", name="database")

# All services (for readiness probe)
full_health = Health()
full_health.postgresql_check("postgresql://localhost/db", name="database") \
           .redis_check("redis://localhost:6379", name="cache") \
           .rabbitmq_check("amqp://localhost:5672", name="queue") \
           .mongodb_check("mongodb://localhost:27017", name="documents")

# Liveness - only checks critical services
app.add_url_rule("/healthz", "liveness", flask_health_endpoint(critical_health))

# Readiness - checks all services
app.add_url_rule("/ready", "readiness", flask_health_endpoint(full_health))

# Detailed health - includes all checks
app.add_url_rule("/health", "health", flask_health_endpoint(full_health))

if __name__ == "__main__":
    app.run(debug=True)
```

## Custom Response Format

Customize the response structure:

```python
from flask import Flask, jsonify
from healthcheckx import Health, overall_status
from datetime import datetime

app = Flask(__name__)
health = Health()

health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://localhost/db")

@app.route("/health")
def health_check():
    results = health.run()
    status = overall_status(results)
    
    # Custom response format
    response_data = {
        "application": "my-flask-api",
        "version": "1.0.0",
        "status": status.value,
        "timestamp": datetime.utcnow().isoformat() + "Z",
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
    
    status_code = 200 if status.value != "unhealthy" else 503
    return jsonify(response_data), status_code

if __name__ == "__main__":
    app.run(debug=True)
```

## Application Factory Pattern

Use Flask application factory with health checks:

```python
from flask import Flask
from healthcheckx import Health, flask_health_endpoint
import os

def create_health():
    """Create and configure health checks"""
    health = Health()
    
    # Add checks based on configuration
    if redis_url := os.getenv("REDIS_URL"):
        health.redis_check(redis_url, name="redis")
    
    if db_url := os.getenv("DATABASE_URL"):
        health.postgresql_check(db_url, name="database")
    
    return health

def create_app(config=None):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    if config:
        app.config.update(config)
    
    # Initialize health checks
    health = create_health()
    
    # Register health endpoint
    app.add_url_rule("/health", "health", flask_health_endpoint(health))
    
    # Register blueprints
    from .api import api_bp
    app.register_blueprint(api_bp)
    
    return app

# Usage
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
```

## Flask Extensions Integration

Integrate with Flask extensions:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from healthcheckx import Health, flask_health_endpoint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/mydb'
app.config['REDIS_URL'] = 'redis://localhost:6379'

# Initialize extensions
db = SQLAlchemy(app)
redis_client = FlaskRedis(app)

# Create health checks using extension connections
health = Health()
health.postgresql_check(app.config['SQLALCHEMY_DATABASE_URI'], name="database") \
      .redis_check(app.config['REDIS_URL'], name="cache")

# Add health endpoint
app.add_url_rule("/health", "health", flask_health_endpoint(health))

@app.route("/")
def index():
    # Use extensions
    users = db.session.query(User).all()
    redis_client.set('key', 'value')
    return {"users": len(users)}

if __name__ == "__main__":
    app.run(debug=True)
```

## Custom Health Checks

Add custom health checks:

```python
from flask import Flask
from healthcheckx import Health, CheckResult, HealthStatus, flask_health_endpoint
import requests

app = Flask(__name__)
health = Health()

# Built-in checks
health.redis_check("redis://localhost:6379")

# Custom check for external API
def external_api_check() -> CheckResult:
    try:
        response = requests.get(
            "https://api.example.com/status",
            timeout=2
        )
        if response.status_code == 200:
            return CheckResult("external-api", HealthStatus.healthy)
        else:
            return CheckResult(
                "external-api",
                HealthStatus.unhealthy,
                f"HTTP {response.status_code}"
            )
    except requests.RequestException as e:
        return CheckResult("external-api", HealthStatus.unhealthy, str(e))

# Custom check for disk space
def disk_space_check() -> CheckResult:
    import shutil
    try:
        total, used, free = shutil.disk_usage("/")
        percent_used = (used / total) * 100
        
        if percent_used > 90:
            return CheckResult(
                "disk-space",
                HealthStatus.unhealthy,
                f"Disk usage at {percent_used:.1f}%"
            )
        elif percent_used > 75:
            return CheckResult(
                "disk-space",
                HealthStatus.degraded,
                f"Disk usage at {percent_used:.1f}%"
            )
        else:
            return CheckResult("disk-space", HealthStatus.healthy)
    except Exception as e:
        return CheckResult("disk-space", HealthStatus.unhealthy, str(e))

# Register custom checks
health.register(external_api_check)
health.register(disk_space_check)

app.add_url_rule("/health", "health", flask_health_endpoint(health))

if __name__ == "__main__":
    app.run(debug=True)
```

## Kubernetes Integration

### Flask App with Probes

```python
from flask import Flask, jsonify
from healthcheckx import Health, flask_health_endpoint

app = Flask(__name__)
health = Health()

health.postgresql_check("postgresql://postgres:5432/db") \
      .redis_check("redis://redis:6379")

# Liveness probe - is the app alive?
@app.route("/healthz")
def liveness():
    return jsonify({"status": "ok"}), 200

# Readiness probe - is the app ready to serve traffic?
app.add_url_rule("/ready", "readiness", flask_health_endpoint(health))

# Startup probe - has the app finished starting?
app.add_url_rule("/startup", "startup", flask_health_endpoint(health))

@app.route("/")
def index():
    return jsonify({"message": "Hello World"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flask-api
  template:
    metadata:
      labels:
        app: flask-api
    spec:
      containers:
      - name: api
        image: flask-api:latest
        ports:
        - containerPort: 5000
        
        env:
        - name: REDIS_URL
          value: "redis://redis:6379"
        - name: DATABASE_URL
          value: "postgresql://postgres:5432/mydb"
        
        # Liveness probe - restart if fails
        livenessProbe:
          httpGet:
            path: /healthz
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        # Readiness probe - remove from service if fails
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        # Startup probe - wait for app to start
        startupProbe:
          httpGet:
            path: /startup
            port: 5000
          initialDelaySeconds: 0
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 30
```

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
  CMD python -c "import requests; requests.get('http://localhost:5000/health').raise_for_status()"

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  flask-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/mydb
    depends_on:
      - redis
      - postgres
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
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

## Production Deployment with Gunicorn

```python
# wsgi.py
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
```

Run with Gunicorn:

```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app
```

Or with configuration file:

```python
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
timeout = 30
keepalive = 5

# Health check
def pre_request(worker, req):
    if req.path == "/health":
        worker.log.debug("Health check request")
```

## Error Handling

Handle errors gracefully:

```python
from flask import Flask, jsonify
from healthcheckx import Health, flask_health_endpoint

app = Flask(__name__)
health = Health()

health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://localhost/db")

app.add_url_rule("/health", "health", flask_health_endpoint(health))

# Global error handler
@app.errorhandler(Exception)
def handle_error(error):
    app.logger.error(f"Error: {error}")
    return jsonify({
        "status": "error",
        "message": str(error)
    }), 500

# Health check shouldn't trigger error handler
@app.errorhandler(503)
def service_unavailable(error):
    # Let health check return 503 without triggering error handler
    return error

if __name__ == "__main__":
    app.run(debug=True)
```

## Logging Integration

Add logging to health checks:

```python
from flask import Flask
from healthcheckx import Health, flask_health_endpoint
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

health = Health()
health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://localhost/db")

# Wrapper to log health checks
def logged_health_endpoint():
    logger.info("Health check initiated")
    health_func = flask_health_endpoint(health)
    response = health_func()
    logger.info(f"Health check completed: {response[1]}")
    return response

app.add_url_rule("/health", "health", logged_health_endpoint)

if __name__ == "__main__":
    app.run(debug=True)
```

## Testing

Test health check endpoints:

```python
# test_health.py
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        yield client

def test_health_endpoint_exists(client):
    """Test that health endpoint exists"""
    response = client.get("/health")
    assert response.status_code in [200, 503]

def test_health_response_format(client):
    """Test health response has correct format"""
    response = client.get("/health")
    data = response.get_json()
    
    assert "status" in data
    assert "checks" in data
    assert isinstance(data["checks"], list)

def test_liveness_probe(client):
    """Test liveness probe always returns 200"""
    response = client.get("/healthz")
    assert response.status_code == 200
    
def test_health_with_mocked_services(client, mocker):
    """Test health with mocked services"""
    # Mock Redis to be healthy
    mocker.patch('redis.Redis.ping', return_value=True)
    
    response = client.get("/health")
    data = response.get_json()
    
    assert data["status"] == "healthy"
```

## Best Practices

1. **Keep It Simple** - Health checks should be fast and straightforward
2. **Separate Concerns** - Use different endpoints for liveness and readiness
3. **Handle Timeouts** - Set appropriate timeouts for all checks (1-3 seconds)
4. **Log Sparingly** - Only log failures or important events
5. **Use Blueprints** - Organize health checks in monitoring blueprint
6. **Production Ready** - Deploy with Gunicorn or uWSGI for production

## Troubleshooting

### Health Endpoint Returns 404

Ensure you're using the helper function correctly:

```python
# ✅ Correct
app.add_url_rule("/health", "health", flask_health_endpoint(health))

# ❌ Wrong
app.add_url_rule("/health", "health", health.run)
```

### Slow Health Checks

If health checks are slow, add timeouts:

```python
health = Health()
# Default timeout is 2 seconds, adjust if needed
health.redis_check("redis://localhost:6379")  # Uses 2s timeout
```

### Import Errors

Make sure healthcheckx is installed with Flask support:

```bash
pip install flask healthcheckx[all]
```

## Next Steps

- [FastAPI Integration](fastapi.md) - FastAPI framework integration
- [Django Integration](django.md) - Django framework integration  
- [Custom Checks](../advanced/custom-checks.md) - Create custom health checks

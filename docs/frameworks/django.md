# Django Integration

Integrate healthcheckx with Django applications for robust health check endpoints.

## Installation

```bash
pip install django healthcheckx[all]
```

## Basic Integration

### Simple Example

1. **Create a health checks module** (`myapp/health.py`):

```python
from healthcheckx import Health
import os

health = Health()

# Register checks from settings
if redis_url := os.getenv("REDIS_URL"):
    health.redis_check(redis_url, name="redis")

if db_url := os.getenv("DATABASE_URL"):
    health.postgresql_check(db_url, name="database")
```

2. **Add view** (`myapp/views.py`):

```python
from healthcheckx import django_health_view
from .health import health

# Create health check view
health_check = django_health_view(health)
```

3. **Configure URL** (`myapp/urls.py`):

```python
from django.urls import path
from .views import health_check

urlpatterns = [
    path('health/', health_check, name='health'),
]
```

4. **Include in main URLs** (`project/urls.py`):

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
]
```

Visit `http://localhost:8000/health/` to see the health status.

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
      "name": "database",
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
      "name": "database",
      "status": "healthy",
      "duration_ms": 38.7
    }
  ]
}
```

## Complete Django Project Setup

### Project Structure

```
myproject/
├── manage.py
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── api/
    ├── __init__.py
    ├── health.py
    ├── views.py
    └── urls.py
```

### Settings Configuration (`settings.py`)

```python
# myproject/settings.py

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',  # Your app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'mydb'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Static files
STATIC_URL = '/static/'
```

### Health Checks Module (`api/health.py`)

```python
from healthcheckx import Health
from django.conf import settings
import os

def create_health():
    """Create health checks based on Django settings"""
    health = Health()
    
    # Database check
    db_config = settings.DATABASES['default']
    if db_config['ENGINE'] == 'django.db.backends.postgresql':
        db_url = (
            f"postgresql://{db_config['USER']}:{db_config['PASSWORD']}"
            f"@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
        )
        health.postgresql_check(db_url, name="database")
    
    elif db_config['ENGINE'] == 'django.db.backends.mysql':
        db_url = (
            f"mysql://{db_config['USER']}:{db_config['PASSWORD']}"
            f"@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
        )
        health.mysql_check(db_url, name="database")
    
    # Cache check
    cache_config = settings.CACHES['default']
    if 'redis' in cache_config['BACKEND'].lower():
        redis_url = cache_config['LOCATION']
        health.redis_check(redis_url, name="cache")
    
    # Additional checks from environment
    if rabbitmq_url := os.getenv("RABBITMQ_URL"):
        health.rabbitmq_check(rabbitmq_url, name="message-queue")
    
    if mongodb_url := os.getenv("MONGODB_URL"):
        health.mongodb_check(mongodb_url, name="mongodb")
    
    return health

# Create singleton instance
health = create_health()
```

### Views (`api/views.py`)

```python
from django.http import JsonResponse
from healthcheckx import django_health_view
from .health import health

# Health check view
health_check = django_health_view(health)

# Liveness probe (simple alive check)
def liveness(request):
    return JsonResponse({"status": "ok"})

# Readiness probe (all services check)
readiness = django_health_view(health)
```

### URL Configuration (`api/urls.py`)

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

### Main URLs (`myproject/urls.py`)

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
]
```

## Using Django ORM Connections

Check database using Django's connection:

```python
# api/health.py
from healthcheckx import Health, CheckResult, HealthStatus
from django.db import connection
from django.conf import settings

health = Health()

def django_db_check() -> CheckResult:
    """Check database using Django's connection"""
    try:
        # Execute simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return CheckResult("django-db", HealthStatus.healthy)
    except Exception as e:
        return CheckResult("django-db", HealthStatus.unhealthy, str(e))

# Register custom check
health.register(django_db_check)

# Also add standard checks
db_config = settings.DATABASES['default']
if db_config['ENGINE'] == 'django.db.backends.postgresql':
    db_url = (
        f"postgresql://{db_config['USER']}:{db_config['PASSWORD']}"
        f"@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
    )
    health.postgresql_check(db_url, name="database")
```

## Django Cache Framework Integration

Check cache using Django's cache:

```python
from healthcheckx import Health, CheckResult, HealthStatus
from django.core.cache import cache

health = Health()

def django_cache_check() -> CheckResult:
    """Check cache using Django's cache framework"""
    try:
        # Test cache set/get
        test_key = "__healthcheck__"
        test_value = "ok"
        
        cache.set(test_key, test_value, 10)
        result = cache.get(test_key)
        cache.delete(test_key)
        
        if result == test_value:
            return CheckResult("django-cache", HealthStatus.healthy)
        else:
            return CheckResult(
                "django-cache",
                HealthStatus.unhealthy,
                "Cache read/write failed"
            )
    except Exception as e:
        return CheckResult("django-cache", HealthStatus.unhealthy, str(e))

health.register(django_cache_check)
```

## Custom Response Format

Create custom health check view:

```python
from django.http import JsonResponse
from healthcheckx import overall_status
from .health import health
from datetime import datetime

def custom_health_view(request):
    """Custom health check with additional metadata"""
    results = health.run()
    status = overall_status(results)
    
    response_data = {
        "application": "my-django-api",
        "version": "1.0.0",
        "status": status.value,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "environment": os.getenv("ENVIRONMENT", "development"),
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
    return JsonResponse(response_data, status=status_code)
```

## Class-Based Views

Use Django class-based views:

```python
from django.views import View
from django.http import JsonResponse
from healthcheckx import overall_status
from .health import health

class HealthCheckView(View):
    """Health check class-based view"""
    
    def get(self, request):
        results = health.run()
        status = overall_status(results)
        
        response_data = {
            "status": status.value,
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
        
        status_code = 200 if status.value != "unhealthy" else 503
        return JsonResponse(response_data, status=status_code)

# In urls.py
from django.urls import path
from .views import HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
]
```

## Django REST Framework Integration

Integrate with Django REST Framework:

```python
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from healthcheckx import overall_status
from .health import health

@api_view(['GET'])
def health_check_view(request):
    """Health check endpoint using DRF"""
    results = health.run()
    health_status = overall_status(results)
    
    response_data = {
        "status": health_status.value,
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
    
    status_code = (
        status.HTTP_200_OK 
        if health_status.value != "unhealthy" 
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    
    return Response(response_data, status=status_code)
```

Or with APIView:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from healthcheckx import overall_status
from .health import health

class HealthCheckAPIView(APIView):
    """Health check API view"""
    
    permission_classes = []  # Public endpoint
    authentication_classes = []  # No auth required
    
    def get(self, request):
        results = health.run()
        health_status = overall_status(results)
        
        response_data = {
            "status": health_status.value,
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
        
        status_code = (
            status.HTTP_200_OK 
            if health_status.value != "unhealthy" 
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        
        return Response(response_data, status=status_code)
```

## Middleware Integration

Create health check middleware:

```python
# api/middleware.py
from django.http import JsonResponse
from healthcheckx import overall_status
from .health import health
import time

class HealthCheckMiddleware:
    """Middleware to log health check requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path == '/health/':
            start_time = time.time()
            response = self.get_response(request)
            duration = time.time() - start_time
            
            # Log health check
            print(f"Health check: {response.status_code} in {duration:.3f}s")
            
            return response
        
        return self.get_response(request)

# Add to settings.py MIDDLEWARE
MIDDLEWARE = [
    # ... other middleware
    'api.middleware.HealthCheckMiddleware',
]
```

## Kubernetes Integration

### Django App with Probes

```python
# api/views.py
from django.http import JsonResponse
from healthcheckx import django_health_view
from .health import health

# Liveness probe - is the app alive?
def liveness(request):
    return JsonResponse({"status": "ok"})

# Readiness probe - is the app ready to serve traffic?
readiness = django_health_view(health)

# Startup probe - has the app finished starting?
startup = django_health_view(health)
```

```python
# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('healthz/', views.liveness, name='liveness'),
    path('ready/', views.readiness, name='readiness'),
    path('startup/', views.startup, name='startup'),
    path('health/', views.readiness, name='health'),
]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: django-api
  template:
    metadata:
      labels:
        app: django-api
    spec:
      containers:
      - name: django
        image: django-api:latest
        ports:
        - containerPort: 8000
        
        env:
        - name: DATABASE_URL
          value: "postgresql://postgres:5432/mydb"
        - name: REDIS_URL
          value: "redis://redis:6379"
        - name: DEBUG
          value: "False"
        
        # Liveness probe - restart if fails
        livenessProbe:
          httpGet:
            path: /healthz/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        # Readiness probe - remove from service if fails
        readinessProbe:
          httpGet:
            path: /ready/
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        # Startup probe - wait for app to start
        startupProbe:
          httpGet:
            path: /startup/
            port: 8000
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

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health/').raise_for_status()"

EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "myproject.wsgi:application"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  django:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_NAME=mydb
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - DB_HOST=postgres
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/1
      - DEBUG=False
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Management Command

Create a management command for health checks:

```python
# api/management/commands/healthcheck.py
from django.core.management.base import BaseCommand
from api.health import health

class Command(BaseCommand):
    help = 'Run health checks'
    
    def handle(self, *args, **options):
        self.stdout.write("Running health checks...")
        
        results = health.run()
        
        for result in results:
            status_color = (
                self.style.SUCCESS if result.status.value == "healthy"
                else self.style.ERROR if result.status.value == "unhealthy"
                else self.style.WARNING
            )
            
            message = f" - {result.message}" if result.message else ""
            self.stdout.write(
                f"{result.name}: {status_color(result.status.value)} "
                f"({result.duration_ms:.2f}ms){message}"
            )
        
        # Exit with error code if unhealthy
        if any(r.status.value == "unhealthy" for r in results):
            raise SystemExit(1)
```

Usage:

```bash
python manage.py healthcheck
```

## Testing

Test health check endpoints:

```python
# api/tests.py
from django.test import TestCase, Client
from django.urls import reverse

class HealthCheckTests(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_health_endpoint_exists(self):
        """Test that health endpoint exists"""
        response = self.client.get('/health/')
        self.assertIn(response.status_code, [200, 503])
    
    def test_health_response_format(self):
        """Test health response has correct format"""
        response = self.client.get('/health/')
        data = response.json()
        
        self.assertIn('status', data)
        self.assertIn('checks', data)
        self.assertIsInstance(data['checks'], list)
    
    def test_liveness_probe(self):
        """Test liveness probe always returns 200"""
        response = self.client.get('/healthz/')
        self.assertEqual(response.status_code, 200)
    
    def test_health_check_view_name(self):
        """Test health check using URL name"""
        url = reverse('api:health')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 503])
```

Run tests:

```bash
python manage.py test api.tests
```

## Best Practices

1. **Use Django Settings** - Configure health checks from Django settings
2. **Separate Probes** - Use different endpoints for liveness and readiness
3. **No Authentication** - Health checks should be publicly accessible
4. **Fast Checks** - Keep total check time under 3 seconds
5. **Use Django ORM** - Leverage Django's connection pooling
6. **Management Commands** - Create commands for CLI health checks
7. **Proper Logging** - Log health check failures for monitoring

## Troubleshooting

### CSRF Token Errors

Health check endpoints should bypass CSRF:

```python
from django.views.decorators.csrf import csrf_exempt
from healthcheckx import django_health_view
from .health import health

@csrf_exempt
def health_check(request):
    return django_health_view(health)(request)
```

### Database Connection Errors

Ensure database settings are correct:

```python
# Check database configuration
python manage.py check --database default
```

### Import Errors

Make sure healthcheckx is installed:

```bash
pip install django healthcheckx[all]
```

## Next Steps

- [FastAPI Integration](fastapi.md) - FastAPI framework integration
- [Flask Integration](flask.md) - Flask framework integration
- [Custom Checks](../advanced/custom-checks.md) - Create custom health checks

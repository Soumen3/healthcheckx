# Custom Health Checks

Create custom health checks for any service or resource in your application.

## Overview

While healthcheckx provides built-in checks for common services, you can easily create custom health checks for:

- External APIs
- File systems
- Custom databases
- Business logic validation
- Third-party services
- Resource availability (disk space, memory, etc.)

## Basic Custom Check

### Simple Function

```python
from healthcheckx import Health, CheckResult, HealthStatus

health = Health()

def custom_api_check() -> CheckResult:
    """Check external API availability"""
    try:
        import requests
        response = requests.get("https://api.example.com/status", timeout=2)
        
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

# Register the custom check
health.register(custom_api_check)

# Run all checks
results = health.run()
```

## CheckResult Structure

The `CheckResult` class has the following parameters:

```python
CheckResult(
    name: str,              # Unique identifier for the check
    status: HealthStatus,   # healthy, unhealthy, or degraded
    message: Optional[str] = None,     # Error or status message
    duration_ms: Optional[float] = None  # Execution time (auto-calculated)
)
```

### HealthStatus Enum

```python
from healthcheckx import HealthStatus

# Available status values:
HealthStatus.healthy    # Service is working correctly
HealthStatus.unhealthy  # Service is down or not working
HealthStatus.degraded   # Service is working but with issues
```

## Advanced Custom Checks

### With Timeout and Retry

```python
from healthcheckx import Health, CheckResult, HealthStatus
import time

def api_check_with_retry() -> CheckResult:
    """Check API with retry logic"""
    import requests
    
    max_retries = 3
    timeout = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                "https://api.example.com/status",
                timeout=timeout
            )
            
            if response.status_code == 200:
                return CheckResult("api", HealthStatus.healthy)
            elif attempt < max_retries - 1:
                time.sleep(0.5)  # Wait before retry
                continue
            else:
                return CheckResult(
                    "api",
                    HealthStatus.unhealthy,
                    f"HTTP {response.status_code}"
                )
        except requests.Timeout:
            if attempt < max_retries - 1:
                continue
            return CheckResult("api", HealthStatus.unhealthy, "Timeout")
        except Exception as e:
            return CheckResult("api", HealthStatus.unhealthy, str(e))
    
    return CheckResult("api", HealthStatus.unhealthy, "All retries failed")

health = Health()
health.register(api_check_with_retry)
```

### Degraded Status Example

```python
from healthcheckx import Health, CheckResult, HealthStatus

def disk_space_check() -> CheckResult:
    """Check disk space with degraded state"""
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
            return CheckResult(
                "disk-space",
                HealthStatus.healthy,
                f"Disk usage: {percent_used:.1f}%"
            )
    except Exception as e:
        return CheckResult("disk-space", HealthStatus.unhealthy, str(e))

health = Health()
health.register(disk_space_check)
```

## Real-World Examples

### 1. External API Health Check

```python
from healthcheckx import Health, CheckResult, HealthStatus
import requests
from typing import Dict, Any

def external_api_check() -> CheckResult:
    """Check external payment gateway API"""
    try:
        response = requests.get(
            "https://payment-gateway.com/api/health",
            headers={"Authorization": "Bearer YOUR_TOKEN"},
            timeout=3
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "operational":
                return CheckResult("payment-gateway", HealthStatus.healthy)
            else:
                return CheckResult(
                    "payment-gateway",
                    HealthStatus.degraded,
                    f"Status: {data.get('status')}"
                )
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

health = Health()
health.register(external_api_check)
```

### 2. S3/Object Storage Check

```python
from healthcheckx import Health, CheckResult, HealthStatus
import boto3
from botocore.exceptions import ClientError

def s3_bucket_check() -> CheckResult:
    """Check S3 bucket accessibility"""
    try:
        s3_client = boto3.client('s3')
        bucket_name = 'my-app-bucket'
        
        # Try to list objects (just check access)
        s3_client.head_bucket(Bucket=bucket_name)
        
        return CheckResult("s3-storage", HealthStatus.healthy)
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            return CheckResult(
                "s3-storage",
                HealthStatus.unhealthy,
                "Bucket not found"
            )
        elif error_code == '403':
            return CheckResult(
                "s3-storage",
                HealthStatus.unhealthy,
                "Access denied"
            )
        else:
            return CheckResult(
                "s3-storage",
                HealthStatus.unhealthy,
                str(e)
            )
    except Exception as e:
        return CheckResult("s3-storage", HealthStatus.unhealthy, str(e))

health = Health()
health.register(s3_bucket_check)
```

### 3. Elasticsearch Check

```python
from healthcheckx import Health, CheckResult, HealthStatus
from elasticsearch import Elasticsearch

def elasticsearch_check() -> CheckResult:
    """Check Elasticsearch cluster health"""
    try:
        es = Elasticsearch(["http://localhost:9200"])
        
        # Get cluster health
        health_info = es.cluster.health()
        cluster_status = health_info['status']
        
        if cluster_status == 'green':
            return CheckResult("elasticsearch", HealthStatus.healthy)
        elif cluster_status == 'yellow':
            return CheckResult(
                "elasticsearch",
                HealthStatus.degraded,
                "Cluster status: yellow"
            )
        else:  # red
            return CheckResult(
                "elasticsearch",
                HealthStatus.unhealthy,
                "Cluster status: red"
            )
    except Exception as e:
        return CheckResult("elasticsearch", HealthStatus.unhealthy, str(e))

health = Health()
health.register(elasticsearch_check)
```

### 4. SMTP Email Service Check

```python
from healthcheckx import Health, CheckResult, HealthStatus
import smtplib

def smtp_check() -> CheckResult:
    """Check SMTP server connectivity"""
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=3)
        server.starttls()
        server.quit()
        
        return CheckResult("smtp", HealthStatus.healthy)
        
    except smtplib.SMTPException as e:
        return CheckResult("smtp", HealthStatus.unhealthy, f"SMTP error: {e}")
    except Exception as e:
        return CheckResult("smtp", HealthStatus.unhealthy, str(e))

health = Health()
health.register(smtp_check)
```

### 5. Memory Usage Check

```python
from healthcheckx import Health, CheckResult, HealthStatus
import psutil

def memory_check() -> CheckResult:
    """Check system memory usage"""
    try:
        memory = psutil.virtual_memory()
        percent_used = memory.percent
        
        if percent_used > 90:
            return CheckResult(
                "memory",
                HealthStatus.unhealthy,
                f"Memory usage critical: {percent_used}%"
            )
        elif percent_used > 75:
            return CheckResult(
                "memory",
                HealthStatus.degraded,
                f"Memory usage high: {percent_used}%"
            )
        else:
            return CheckResult(
                "memory",
                HealthStatus.healthy,
                f"Memory usage: {percent_used}%"
            )
    except Exception as e:
        return CheckResult("memory", HealthStatus.unhealthy, str(e))

health = Health()
health.register(memory_check)
```

### 6. WebSocket Connection Check

```python
from healthcheckx import Health, CheckResult, HealthStatus
import websocket

def websocket_check() -> CheckResult:
    """Check WebSocket server connectivity"""
    try:
        ws = websocket.create_connection(
            "ws://localhost:8080/ws",
            timeout=2
        )
        
        # Send ping
        ws.send("ping")
        response = ws.recv()
        ws.close()
        
        if response == "pong":
            return CheckResult("websocket", HealthStatus.healthy)
        else:
            return CheckResult(
                "websocket",
                HealthStatus.degraded,
                f"Unexpected response: {response}"
            )
    except Exception as e:
        return CheckResult("websocket", HealthStatus.unhealthy, str(e))

health = Health()
health.register(websocket_check)
```

### 7. Custom Database Query Check

```python
from healthcheckx import Health, CheckResult, HealthStatus
import psycopg2

def business_logic_check() -> CheckResult:
    """Check if critical data exists"""
    try:
        conn = psycopg2.connect(
            "postgresql://user:pass@localhost/db",
            connect_timeout=2
        )
        cursor = conn.cursor()
        
        # Check if admin user exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        if admin_count > 0:
            return CheckResult("admin-users", HealthStatus.healthy)
        else:
            return CheckResult(
                "admin-users",
                HealthStatus.unhealthy,
                "No admin users found"
            )
    except Exception as e:
        return CheckResult("admin-users", HealthStatus.unhealthy, str(e))

health = Health()
health.register(business_logic_check)
```

### 8. Certificate Expiry Check

```python
from healthcheckx import Health, CheckResult, HealthStatus
import ssl
import socket
from datetime import datetime, timedelta

def ssl_certificate_check() -> CheckResult:
    """Check SSL certificate expiry"""
    try:
        hostname = "example.com"
        context = ssl.create_default_context()
        
        with socket.create_connection((hostname, 443), timeout=2) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
        
        # Parse expiry date
        expiry_date = datetime.strptime(
            cert['notAfter'],
            '%b %d %H:%M:%S %Y %Z'
        )
        days_until_expiry = (expiry_date - datetime.now()).days
        
        if days_until_expiry < 7:
            return CheckResult(
                "ssl-cert",
                HealthStatus.unhealthy,
                f"Certificate expires in {days_until_expiry} days"
            )
        elif days_until_expiry < 30:
            return CheckResult(
                "ssl-cert",
                HealthStatus.degraded,
                f"Certificate expires in {days_until_expiry} days"
            )
        else:
            return CheckResult("ssl-cert", HealthStatus.healthy)
            
    except Exception as e:
        return CheckResult("ssl-cert", HealthStatus.unhealthy, str(e))

health = Health()
health.register(ssl_certificate_check)
```

## Parameterized Custom Checks

Create reusable check functions with parameters:

```python
from healthcheckx import Health, CheckResult, HealthStatus
import requests
from typing import Callable

def create_http_check(
    name: str,
    url: str,
    timeout: int = 2,
    expected_status: int = 200
) -> Callable[[], CheckResult]:
    """Factory function to create HTTP health checks"""
    
    def check() -> CheckResult:
        try:
            response = requests.get(url, timeout=timeout)
            
            if response.status_code == expected_status:
                return CheckResult(name, HealthStatus.healthy)
            else:
                return CheckResult(
                    name,
                    HealthStatus.unhealthy,
                    f"Expected {expected_status}, got {response.status_code}"
                )
        except Exception as e:
            return CheckResult(name, HealthStatus.unhealthy, str(e))
    
    return check

# Create multiple checks using the factory
health = Health()

health.register(create_http_check(
    "api-users",
    "https://api.example.com/users"
))

health.register(create_http_check(
    "api-products",
    "https://api.example.com/products"
))

health.register(create_http_check(
    "admin-panel",
    "https://admin.example.com",
    timeout=3
))
```

## Class-Based Custom Checks

Use classes for more complex checks:

```python
from healthcheckx import Health, CheckResult, HealthStatus
import requests
from typing import Optional

class ApiHealthCheck:
    """Reusable API health check with state"""
    
    def __init__(
        self,
        name: str,
        url: str,
        timeout: int = 2,
        headers: Optional[dict] = None
    ):
        self.name = name
        self.url = url
        self.timeout = timeout
        self.headers = headers or {}
        self.last_check_time = None
        self.failure_count = 0
    
    def __call__(self) -> CheckResult:
        """Make the class callable for health check"""
        try:
            response = requests.get(
                self.url,
                timeout=self.timeout,
                headers=self.headers
            )
            
            if response.status_code == 200:
                self.failure_count = 0
                return CheckResult(self.name, HealthStatus.healthy)
            else:
                self.failure_count += 1
                return CheckResult(
                    self.name,
                    HealthStatus.unhealthy,
                    f"HTTP {response.status_code} (failures: {self.failure_count})"
                )
        except Exception as e:
            self.failure_count += 1
            return CheckResult(
                self.name,
                HealthStatus.unhealthy,
                f"{str(e)} (failures: {self.failure_count})"
            )

# Usage
health = Health()

api_check = ApiHealthCheck(
    "payment-api",
    "https://payment.example.com/health",
    headers={"Authorization": "Bearer TOKEN"}
)

health.register(api_check)
```

## Async Custom Checks

For async operations (use with FastAPI):

```python
from healthcheckx import Health, CheckResult, HealthStatus
import asyncio
import aiohttp

async def async_api_check() -> CheckResult:
    """Async HTTP check"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.example.com/status",
                timeout=aiohttp.ClientTimeout(total=2)
            ) as response:
                if response.status == 200:
                    return CheckResult("async-api", HealthStatus.healthy)
                else:
                    return CheckResult(
                        "async-api",
                        HealthStatus.unhealthy,
                        f"HTTP {response.status}"
                    )
    except Exception as e:
        return CheckResult("async-api", HealthStatus.unhealthy, str(e))

# Sync wrapper for healthcheckx
def sync_api_check() -> CheckResult:
    return asyncio.run(async_api_check())

health = Health()
health.register(sync_api_check)
```

## Error Handling Best Practices

### Comprehensive Error Handling

```python
from healthcheckx import Health, CheckResult, HealthStatus
import logging

logger = logging.getLogger(__name__)

def robust_check() -> CheckResult:
    """Health check with comprehensive error handling"""
    check_name = "my-service"
    
    try:
        # Your check logic here
        # ...
        
        return CheckResult(check_name, HealthStatus.healthy)
        
    except TimeoutError as e:
        logger.warning(f"{check_name} check timeout: {e}")
        return CheckResult(
            check_name,
            HealthStatus.unhealthy,
            "Timeout"
        )
    except ConnectionError as e:
        logger.error(f"{check_name} connection failed: {e}")
        return CheckResult(
            check_name,
            HealthStatus.unhealthy,
            "Connection failed"
        )
    except Exception as e:
        logger.exception(f"{check_name} unexpected error")
        return CheckResult(
            check_name,
            HealthStatus.unhealthy,
            f"Error: {type(e).__name__}"
        )

health = Health()
health.register(robust_check)
```

## Testing Custom Checks

Write unit tests for custom checks:

```python
import unittest
from healthcheckx import HealthStatus

class TestCustomChecks(unittest.TestCase):
    def test_disk_space_healthy(self):
        """Test disk space check returns healthy when space available"""
        result = disk_space_check()
        self.assertEqual(result.name, "disk-space")
        self.assertIn(result.status, [
            HealthStatus.healthy,
            HealthStatus.degraded,
            HealthStatus.unhealthy
        ])
    
    def test_api_check_handles_timeout(self):
        """Test API check handles timeout gracefully"""
        result = api_check_with_retry()
        self.assertIsNotNone(result)
        self.assertIsInstance(result.status, HealthStatus)
    
    def test_check_result_structure(self):
        """Test CheckResult has required fields"""
        result = custom_api_check()
        self.assertIsNotNone(result.name)
        self.assertIsNotNone(result.status)
        self.assertIsInstance(result.duration_ms, (int, float, type(None)))

if __name__ == '__main__':
    unittest.main()
```

## Best Practices

1. **Always Return CheckResult** - Never raise exceptions, always return a CheckResult
2. **Set Timeouts** - Always use timeouts to prevent hanging checks
3. **Meaningful Names** - Use descriptive names for check identification
4. **Clear Messages** - Provide helpful error messages for troubleshooting
5. **Use Degraded Status** - Distinguish between complete failure and degraded service
6. **Keep It Fast** - Aim for checks to complete in under 2 seconds
7. **Log Failures** - Log detailed errors for debugging
8. **Test Your Checks** - Write unit tests for custom check logic
9. **Handle All Exceptions** - Catch and handle all possible exceptions
10. **Don't Modify State** - Health checks should be read-only operations

## Common Patterns

### Retry Pattern

```python
def check_with_retry(max_retries: int = 3) -> CheckResult:
    for attempt in range(max_retries):
        try:
            # Check logic
            return CheckResult("service", HealthStatus.healthy)
        except Exception as e:
            if attempt == max_retries - 1:
                return CheckResult("service", HealthStatus.unhealthy, str(e))
            time.sleep(0.5)
```

### Circuit Breaker Pattern

```python
class CircuitBreakerCheck:
    def __init__(self, threshold: int = 5):
        self.failure_count = 0
        self.threshold = threshold
        self.is_open = False
    
    def __call__(self) -> CheckResult:
        if self.is_open:
            return CheckResult("service", HealthStatus.unhealthy, "Circuit open")
        
        try:
            # Check logic
            self.failure_count = 0
            return CheckResult("service", HealthStatus.healthy)
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= self.threshold:
                self.is_open = True
            return CheckResult("service", HealthStatus.unhealthy, str(e))
```

## Next Steps

- [Multiple Instances](multiple-instances.md) - Check multiple instances of the same service
- [Configuration](configuration.md) - Configure timeouts and behavior
- [Examples](../examples.md) - More complete examples

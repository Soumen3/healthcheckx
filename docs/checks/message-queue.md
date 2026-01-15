# Message Queues

Health checks for message queue systems.

## RabbitMQ

RabbitMQ is a robust message broker supporting multiple messaging protocols.

### Basic Usage

```python
from healthcheckx import Health

health = Health()
health.rabbitmq_check("amqp://guest:guest@localhost:5672")

results = health.run()
```

### Connection Formats

```python
# Basic with default credentials
health.rabbitmq_check("amqp://guest:guest@localhost:5672")

# With custom credentials
health.rabbitmq_check("amqp://myuser:mypassword@rabbitmq.example.com:5672")

# With virtual host
health.rabbitmq_check("amqp://user:pass@localhost:5672/my_vhost")

# With SSL/TLS
health.rabbitmq_check("amqps://user:pass@secure.example.com:5671")
```

### Custom Timeout

```python
health.rabbitmq_check(
    "amqp://guest:guest@localhost:5672",
    timeout=3
)
```

### Multiple RabbitMQ Instances

```python
health.rabbitmq_check(
    "amqp://user:pass@primary:5672",
    name="rabbitmq-primary"
)

health.rabbitmq_check(
    "amqp://user:pass@secondary:5672",
    name="rabbitmq-secondary"
)
```

### Complete Example

```python
from healthcheckx import Health, overall_status

health = Health()

# Production setup
health.rabbitmq_check(
    "amqp://app_user:secure_pass@rabbitmq-prod.example.com:5672/production",
    timeout=3,
    name="rabbitmq-prod"
)

# Development setup
health.rabbitmq_check(
    "amqp://guest:guest@localhost:5672",
    timeout=2,
    name="rabbitmq-dev"
)

results = health.run()
status = overall_status(results)

for result in results:
    print(f"{result.name}: {result.status} ({result.duration_ms:.2f}ms)")
    if result.message:
        print(f"  Error: {result.message}")

print(f"\nOverall Status: {status}")
```

### Installation

```bash
pip install healthcheckx[rabbitmq]
```

### How It Works

The RabbitMQ health check:
1. Connects to the RabbitMQ server using the AMQP protocol
2. Opens a connection and channel
3. Verifies the connection is active
4. Closes the connection cleanly
5. Returns `healthy` if all steps succeed
6. Returns `unhealthy` if connection fails or times out

### Parameters

- **`amqp_url`** (str): AMQP connection URL
  - Format: `amqp://username:password@host:port/vhost`
  - Default port: 5672 (5671 for amqps)
  
- **`timeout`** (int, optional): Connection timeout in seconds
  - Default: 2
  - Recommended: 2-5 seconds
  
- **`name`** (str, optional): Custom name for the check
  - Default: "rabbitmq"
  - Use for multiple instances

### Environment Variables Example

```python
import os
from healthcheckx import Health

health = Health()

rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672")
health.rabbitmq_check(rabbitmq_url)

results = health.run()
```

## Best Practices

1. **Use specific virtual hosts** - Don't use the default `/` vhost in production
2. **Create dedicated health check users** - Use limited-privilege users for health checks
3. **Set appropriate timeouts** - Message queue checks should be fast (2-3 seconds)
4. **Monitor all nodes** - In a cluster, check each node separately
5. **Check both publishers and consumers** - Health check verifies connection, not message flow

## Common Issues

### Authentication Failed

```
Error: Authentication failed
```

**Solution:** Verify username and password in the connection URL

```python
# Correct format
health.rabbitmq_check("amqp://correct_user:correct_pass@localhost:5672")
```

### Connection Refused

```
Error: Connection refused
```

**Solution:** 
- Verify RabbitMQ is running
- Check firewall rules
- Verify the port (default: 5672)

```bash
# Check if RabbitMQ is running
rabbitmqctl status
```

### Virtual Host Not Found

```
Error: Virtual host '/my_vhost' not found
```

**Solution:** Create the virtual host or use an existing one

```bash
# Create virtual host
rabbitmqctl add_vhost /my_vhost
rabbitmqctl set_permissions -p /my_vhost myuser ".*" ".*" ".*"
```

### Timeout

```
Error: Connection timeout
```

**Solution:** Increase timeout or check network connectivity

```python
health.rabbitmq_check(
    "amqp://user:pass@remote:5672",
    timeout=5  # Increased timeout
)
```

## Advanced Configuration

### With Management Plugin

If you have the RabbitMQ management plugin, you can also create HTTP-based health checks:

```python
from healthcheckx import Health, CheckResult, HealthStatus
import requests

def rabbitmq_management_check():
    """Check RabbitMQ via management API"""
    try:
        response = requests.get(
            "http://localhost:15672/api/healthchecks/node",
            auth=("guest", "guest"),
            timeout=2
        )
        if response.status_code == 200:
            return CheckResult("rabbitmq-mgmt", HealthStatus.healthy)
        else:
            return CheckResult(
                "rabbitmq-mgmt",
                HealthStatus.unhealthy,
                f"HTTP {response.status_code}"
            )
    except Exception as e:
        return CheckResult("rabbitmq-mgmt", HealthStatus.unhealthy, str(e))

health = Health()
health.register(rabbitmq_management_check)
health.rabbitmq_check("amqp://guest:guest@localhost:5672")

results = health.run()
```

### Cluster Monitoring

Monitor all nodes in a RabbitMQ cluster:

```python
from healthcheckx import Health

health = Health()

cluster_nodes = [
    ("amqp://user:pass@node1:5672", "rabbitmq-node1"),
    ("amqp://user:pass@node2:5672", "rabbitmq-node2"),
    ("amqp://user:pass@node3:5672", "rabbitmq-node3"),
]

for url, name in cluster_nodes:
    health.rabbitmq_check(url, name=name)

results = health.run()

# Check cluster health
healthy_nodes = sum(1 for r in results if r.status == "healthy")
total_nodes = len(results)

print(f"Cluster Status: {healthy_nodes}/{total_nodes} nodes healthy")
```

## Docker Compose Example

```yaml
version: '3.8'

services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: myuser
      RABBITMQ_DEFAULT_PASS: mypassword
    healthcheck:
      test: rabbitmq-diagnostics -q ping
      interval: 30s
      timeout: 10s
      retries: 3
```

Python health check for this setup:

```python
health.rabbitmq_check("amqp://myuser:mypassword@localhost:5672")
```

## Next Steps

- [Relational Database Checks](relational-db.md) - Database health checks
- [NoSQL Checks](nosql.md) - NoSQL database health checks
- [Custom Checks](../advanced/custom-checks.md) - Create custom message queue checks

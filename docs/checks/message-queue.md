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

## Kafka

Apache Kafka is a distributed event streaming platform.

### Basic Usage

```python
from healthcheckx import Health

health = Health()
health.kafka_check("localhost:9092")

results = health.run()
```

### Connection Formats

```python
# Single broker
health.kafka_check("localhost:9092")

# Multiple brokers (cluster)
health.kafka_check("broker1:9092,broker2:9092,broker3:9092")

# With custom name
health.kafka_check("kafka.example.com:9092", name="kafka-prod")
```

### Custom Timeout

```python
health.kafka_check(
    "localhost:9092",
    timeout=3
)
```

### Multiple Kafka Clusters

```python
health.kafka_check(
    "prod-broker1:9092,prod-broker2:9092",
    name="kafka-production"
)

health.kafka_check(
    "dev-broker:9092",
    name="kafka-development"
)
```

### Complete Example

```python
from healthcheckx import Health, overall_status

health = Health()

# Production Kafka cluster
health.kafka_check(
    "kafka1.prod.example.com:9092,kafka2.prod.example.com:9092,kafka3.prod.example.com:9092",
    timeout=3,
    name="kafka-prod-cluster"
)

# Development Kafka
health.kafka_check(
    "localhost:9092",
    timeout=2,
    name="kafka-dev"
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
pip install healthcheckx[kafka]
```

### How It Works

The Kafka health check:
1. Creates a KafkaAdminClient with the provided bootstrap servers
2. Attempts to retrieve cluster metadata
3. Verifies connection to at least one broker
4. Closes the client connection
5. Returns `healthy` if metadata retrieval succeeds
6. Returns `unhealthy` if connection fails or times out

### Parameters

- **`bootstrap_servers`** (str): Comma-separated list of Kafka broker addresses
  - Format: `host:port` or `host1:port1,host2:port2`
  - Default port: 9092
  
- **`timeout`** (int, optional): Connection timeout in seconds
  - Default: 2
  - Recommended: 2-5 seconds
  
- **`name`** (str, optional): Custom name for the check
  - Default: "kafka"
  - Use for multiple clusters

### Environment Variables Example

```python
import os
from healthcheckx import Health

health = Health()

kafka_brokers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
health.kafka_check(kafka_brokers)

results = health.run()
```

### Docker Compose Example

```yaml
version: '3.8'

services:
  kafka:
    image: confluentinc/cp-kafka:latest
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
```

Python health check for this setup:

```python
health.kafka_check("localhost:9092")
```

---

## ActiveMQ

Apache ActiveMQ is a popular open-source message broker supporting multiple protocols.

### Basic Usage

```python
from healthcheckx import Health

health = Health()
# Using OpenWire protocol (TCP)
health.activemq_check("tcp://localhost:61616")

results = health.run()
```

### Connection Formats

```python
# OpenWire protocol (default port 61616)
health.activemq_check("tcp://localhost:61616")

# STOMP protocol (default port 61613)
health.activemq_check("stomp://localhost:61613")

# With custom name
health.activemq_check("tcp://activemq.example.com:61616", name="activemq-prod")
```

### Custom Timeout

```python
health.activemq_check(
    "tcp://localhost:61616",
    timeout=3
)
```

### Multiple ActiveMQ Instances

```python
health.activemq_check(
    "tcp://primary:61616",
    name="activemq-primary"
)

health.activemq_check(
    "tcp://secondary:61616",
    name="activemq-secondary"
)
```

### Complete Example

```python
from healthcheckx import Health, overall_status

health = Health()

# OpenWire protocol check
health.activemq_check(
    "tcp://activemq-prod.example.com:61616",
    timeout=3,
    name="activemq-openwire"
)

# STOMP protocol check
health.activemq_check(
    "stomp://activemq-prod.example.com:61613",
    timeout=3,
    name="activemq-stomp"
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
pip install healthcheckx[activemq]
```

### How It Works

The ActiveMQ health check supports two protocols:

**TCP (OpenWire) Check:**
1. Parses the broker URL for host and port
2. Creates a TCP socket connection
3. Attempts to connect to the broker
4. Returns `healthy` if connection succeeds
5. Returns `unhealthy` if connection fails or times out

**STOMP Check:**
1. Parses the broker URL for host and port
2. Creates a STOMP connection
3. Attempts to connect to the broker
4. Returns `healthy` if connection succeeds
5. Returns `unhealthy` if connection fails or times out

### Parameters

- **`broker_url`** (str): ActiveMQ broker URL
  - TCP format: `tcp://host:port` (default port: 61616)
  - STOMP format: `stomp://host:port` (default port: 61613)
  
- **`timeout`** (int, optional): Connection timeout in seconds
  - Default: 2
  - Recommended: 2-5 seconds
  
- **`name`** (str, optional): Custom name for the check
  - Default: "activemq"
  - Use for multiple instances or protocols

### Environment Variables Example

```python
import os
from healthcheckx import Health

health = Health()

activemq_url = os.getenv("ACTIVEMQ_BROKER_URL", "tcp://localhost:61616")
health.activemq_check(activemq_url)

results = health.run()
```

### Docker Compose Example

```yaml
version: '3.8'

services:
  activemq:
    image: apache/activemq-classic:latest
    ports:
      - "61616:61616"  # OpenWire
      - "61613:61613"  # STOMP
      - "8161:8161"    # Web Console
```

Python health check for this setup:

```python
# Check OpenWire protocol
health.activemq_check("tcp://localhost:61616", name="activemq-openwire")

# Check STOMP protocol
health.activemq_check("stomp://localhost:61613", name="activemq-stomp")
```

---

## Best Practices

1. **Use specific names** - When monitoring multiple instances, use descriptive names
2. **Set appropriate timeouts** - Message queue checks should be fast (2-3 seconds)
3. **Monitor all brokers** - In a cluster, check each broker/node separately
4. **Check connectivity only** - Health checks verify connection, not message processing
5. **Use environment variables** - Store connection URLs in environment variables

## Common Issues

### Connection Refused

```
Error: Connection refused
```

**Solution:**
- Verify the message broker is running
- Check host and port
- Verify firewall rules
- Ensure correct protocol (AMQP/Kafka/TCP/STOMP)

### Authentication Failed

```
Error: Authentication failed
```

**Solution:**
- Verify username and password
- Check user permissions
- Verify authentication configuration

### Timeout

```
Error: Connection timeout
```

**Solution:**
- Increase timeout value
- Check network connectivity
- Verify broker is not overloaded

### Protocol Mismatch

```
Error: Protocol error
```

**Solution for ActiveMQ:**
- Use `tcp://` for OpenWire (port 61616)
- Use `stomp://` for STOMP (port 61613)
- Use `amqp://` for AMQP (use rabbitmq_check)

## Comparison Table

| Message Queue | Default Port | Protocol | Check Method |
|---------------|-------------|----------|--------------|
| RabbitMQ | 5672 | AMQP | Connection + Channel |
| Kafka | 9092 | Kafka Native | Cluster Metadata |
| ActiveMQ (OpenWire) | 61616 | TCP/OpenWire | TCP Socket |
| ActiveMQ (STOMP) | 61613 | STOMP | STOMP Connection |

---

## Next Steps

- [Cache Checks](cache.md) - Redis, KeyDB, Memcached
- [Relational Database Checks](relational-db.md) - PostgreSQL, MySQL, etc.
- [NoSQL Checks](nosql.md) - MongoDB health checks
- [Custom Checks](../advanced/custom-checks.md) - Create custom message queue checks

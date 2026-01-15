# Cache Systems

Health checks for caching systems including Redis, KeyDB, and Memcached.

## Redis

Redis is an in-memory data structure store used as a database, cache, and message broker.

### Basic Usage

```python
from healthcheckx import Health

health = Health()
health.redis_check("redis://localhost:6379")

results = health.run()
```

### With Authentication

```python
health.redis_check("redis://username:password@localhost:6379/0")
```

### Custom Timeout

```python
health.redis_check("redis://localhost:6379", timeout=3)
```

### Custom Name

```python
# Monitor multiple Redis instances
health.redis_check("redis://primary:6379", name="redis-primary")
health.redis_check("redis://cache:6379", name="redis-cache")
health.redis_check("redis://sessions:6379", name="redis-sessions")
```

### Connection Formats

```python
# Basic
health.redis_check("redis://localhost:6379")

# With database number
health.redis_check("redis://localhost:6379/1")

# With authentication
health.redis_check("redis://user:pass@localhost:6379")

# Redis Sentinel
health.redis_check("redis://sentinel1:26379,sentinel2:26379/mymaster")

# Unix socket
health.redis_check("redis:///var/run/redis.sock")
```

### Installation

```bash
pip install healthcheckx[redis]
```

### How It Works

The Redis health check:
1. Connects to the Redis server using the provided URL
2. Executes a `PING` command
3. Returns `healthy` if ping succeeds
4. Returns `unhealthy` if connection fails or times out

---

## KeyDB

KeyDB is a Redis-compatible in-memory database with enhanced performance features.

### Basic Usage

```python
from healthcheckx import Health

health = Health()
health.keydb_check("keydb://localhost:6379")

results = health.run()
```

### Connection Formats

```python
# Using keydb:// scheme
health.keydb_check("keydb://localhost:6379")

# Using redis:// scheme (also works)
health.keydb_check("redis://localhost:6379")

# With authentication
health.keydb_check("keydb://user:password@localhost:6379/0")
```

### Multiple KeyDB Instances

```python
health.keydb_check("keydb://node1:6379", name="keydb-node1")
health.keydb_check("keydb://node2:6379", name="keydb-node2")
health.keydb_check("keydb://node3:6379", name="keydb-node3")
```

### Installation

```bash
# KeyDB uses the same client as Redis
pip install healthcheckx[redis]
```

### Notes

- KeyDB is 100% Redis-compatible
- Uses the same `redis` Python library
- Supports all Redis connection features
- Can use either `keydb://` or `redis://` URL schemes

---

## Memcached

Memcached is a high-performance, distributed memory object caching system.

### Basic Usage

```python
from healthcheckx import Health

health = Health()
health.memcached_check()  # Defaults to localhost:11211

results = health.run()
```

### Custom Host and Port

```python
health.memcached_check(host="cache.example.com", port=11211)
```

### With Timeout

```python
health.memcached_check(
    host="localhost",
    port=11211,
    timeout=3
)
```

### Multiple Memcached Servers

```python
health.memcached_check(host="cache1.local", port=11211, name="memcached-1")
health.memcached_check(host="cache2.local", port=11211, name="memcached-2")
health.memcached_check(host="cache3.local", port=11211, name="memcached-3")
```

### Complete Example

```python
from healthcheckx import Health

health = Health()

# Single instance
health.memcached_check()

# Multiple instances with custom configuration
health.memcached_check(
    host="cache-primary.example.com",
    port=11211,
    timeout=2,
    name="cache-primary"
)

health.memcached_check(
    host="cache-secondary.example.com",
    port=11211,
    timeout=2,
    name="cache-secondary"
)

results = health.run()

for result in results:
    print(f"{result.name}: {result.status} ({result.duration_ms:.2f}ms)")
```

### Installation

```bash
pip install healthcheckx[memcached]
```

### How It Works

The Memcached health check:
1. Connects to the Memcached server
2. Executes a `stats` command
3. Returns `healthy` if stats are retrieved successfully
4. Returns `unhealthy` if connection fails or times out

---

## Comparison

| Feature | Redis | KeyDB | Memcached |
|---------|-------|-------|-----------|
| **URL-based config** | ✅ Yes | ✅ Yes | ❌ No (host/port) |
| **Authentication** | ✅ Yes | ✅ Yes | ❌ No |
| **Default port** | 6379 | 6379 | 11211 |
| **Check method** | PING | PING | stats |
| **Installation** | `[redis]` | `[redis]` | `[memcached]` |

## Best Practices

1. **Set appropriate timeouts** - Cache checks should be fast (1-3 seconds)
2. **Use named checks** - When monitoring multiple instances, always use the `name` parameter
3. **Monitor read replicas** - Check both primary and replica instances
4. **Connection pooling** - healthcheckx creates new connections for each check
5. **Production monitoring** - Combine with metrics to track check duration over time

## Common Issues

### Connection Refused

```python
# Error: Connection refused
# Solution: Verify service is running and accessible
health.redis_check("redis://localhost:6379", timeout=1)
```

### Authentication Failed

```python
# Error: Authentication required / Invalid password
# Solution: Check credentials in connection string
health.redis_check("redis://user:correct_password@localhost:6379")
```

### Timeout

```python
# Error: Connection timeout
# Solution: Increase timeout or check network connectivity
health.redis_check("redis://slow-server:6379", timeout=5)
```

## Next Steps

- [Message Queue Checks](message-queue.md) - RabbitMQ health checks
- [Relational DB Checks](relational-db.md) - Database health checks
- [Custom Checks](../advanced/custom-checks.md) - Create your own cache checks

# NoSQL Databases

Health checks for NoSQL database systems.

## MongoDB

MongoDB is a document-oriented NoSQL database.

### Basic Usage

```python
from healthcheckx import Health

health = Health()
health.mongodb_check("mongodb://localhost:27017")

results = health.run()
```

### Connection Formats

```python
# Local MongoDB
health.mongodb_check("mongodb://localhost:27017")

# With database
health.mongodb_check("mongodb://localhost:27017/mydb")

# With authentication
health.mongodb_check("mongodb://user:password@localhost:27017/mydb")

# MongoDB Atlas (Cloud)
health.mongodb_check("mongodb+srv://user:pass@cluster.mongodb.net/mydb")

# Replica Set
health.mongodb_check("mongodb://host1:27017,host2:27017,host3:27017/?replicaSet=myReplicaSet")

# With options
health.mongodb_check("mongodb://localhost:27017/mydb?authSource=admin&retryWrites=true")
```

### Custom Timeout

```python
health.mongodb_check(
    "mongodb://localhost:27017",
    timeout=3
)
```

### Custom Name

```python
# Multiple MongoDB instances
health.mongodb_check(
    "mongodb://primary:27017",
    name="mongo-primary"
)

health.mongodb_check(
    "mongodb://secondary:27017",
    name="mongo-secondary"
)
```

### Installation

```bash
pip install healthcheckx[mongodb]
```

### How It Works

The MongoDB health check:
1. Creates a MongoClient with specified timeout
2. Executes `ping` command on admin database
3. Closes the connection
4. Returns `healthy` if ping succeeds
5. Returns `unhealthy` if connection fails or times out

### Complete Example

```python
from healthcheckx import Health, overall_status
import os

health = Health()

# Production cluster
health.mongodb_check(
    os.getenv("MONGO_PROD_URL", "mongodb://prod-cluster:27017/production"),
    timeout=3,
    name="mongo-prod"
)

# Analytics database
health.mongodb_check(
    os.getenv("MONGO_ANALYTICS_URL", "mongodb://analytics:27017/analytics"),
    timeout=3,
    name="mongo-analytics"
)

# Local development
health.mongodb_check(
    "mongodb://localhost:27017/dev",
    timeout=2,
    name="mongo-dev"
)

results = health.run()
status = overall_status(results)

print(f"MongoDB Health Status: {status}\n")
for result in results:
    status_emoji = "✅" if result.status == "healthy" else "❌"
    print(f"{status_emoji} {result.name}: {result.status} ({result.duration_ms:.2f}ms)")
    if result.message:
        print(f"   Error: {result.message}")
```

## MongoDB Atlas (Cloud) Example

```python
from healthcheckx import Health

# Atlas connection string
atlas_uri = "mongodb+srv://username:password@cluster0.mongodb.net/mydb?retryWrites=true&w=majority"

health = Health()
health.mongodb_check(atlas_uri, timeout=5, name="mongodb-atlas")

results = health.run()
```

## Replica Set Monitoring

Monitor all members of a replica set:

```python
from healthcheckx import Health

health = Health()

replica_set_members = [
    ("mongodb://primary:27017", "mongo-primary"),
    ("mongodb://secondary1:27017", "mongo-secondary1"),
    ("mongodb://secondary2:27017", "mongo-secondary2"),
]

for uri, name in replica_set_members:
    health.mongodb_check(uri, timeout=3, name=name)

results = health.run()

# Check replica set health
healthy_members = sum(1 for r in results if r.status == "healthy")
total_members = len(results)

print(f"Replica Set: {healthy_members}/{total_members} members healthy")
```

## Connection String Options

Common MongoDB connection string options:

```python
# Authentication database
health.mongodb_check("mongodb://user:pass@host/mydb?authSource=admin")

# SSL/TLS
health.mongodb_check("mongodb://host/db?ssl=true&tlsAllowInvalidCertificates=true")

# Read preference
health.mongodb_check("mongodb://host/db?readPreference=secondary")

# Write concern
health.mongodb_check("mongodb://host/db?w=majority")

# Retry writes
health.mongodb_check("mongodb://host/db?retryWrites=true")
```

## Best Practices

### 1. Set Appropriate Timeouts

```python
# Local MongoDB
health.mongodb_check("mongodb://localhost:27017", timeout=2)

# Remote/Cloud MongoDB
health.mongodb_check("mongodb+srv://cluster.mongodb.net/db", timeout=5)
```

### 2. Monitor All Replica Set Members

```python
# Don't just check the connection string
# Check each member individually
for member in replica_set_members:
    health.mongodb_check(member, name=f"mongo-{member}")
```

### 3. Use Read-Only Operations

Health checks only perform ping operations and don't modify data.

### 4. Authentication

Always use authentication in production:

```python
# ❌ Not recommended for production
health.mongodb_check("mongodb://localhost:27017/mydb")

# ✅ Recommended
health.mongodb_check("mongodb://app_user:secure_pass@localhost:27017/mydb?authSource=admin")
```

### 5. Environment Variables

```python
import os

mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/dev")
health.mongodb_check(mongo_url)
```

## Common Issues

### Connection Refused

```
Error: Connection refused
```

**Solutions:**
- Verify MongoDB is running: `systemctl status mongod`
- Check port (default: 27017)
- Verify firewall rules

### Authentication Failed

```
Error: Authentication failed
```

**Solutions:**
- Verify username and password
- Check authentication database: `?authSource=admin`
- Verify user permissions

```javascript
// In MongoDB shell
use admin
db.createUser({
  user: "myuser",
  pwd: "mypassword",
  roles: [ { role: "readWrite", db: "mydb" } ]
})
```

### Server Selection Timeout

```
Error: Server selection timeout
```

**Solutions:**
- Increase timeout
- Check network connectivity
- Verify MongoDB is accepting connections

```python
health.mongodb_check(
    "mongodb://remote-host:27017",
    timeout=10  # Increased timeout
)
```

### SSL/TLS Errors

```
Error: SSL handshake failed
```

**Solutions:**
```python
# Allow invalid certificates (development only)
health.mongodb_check("mongodb://host/db?ssl=true&tlsAllowInvalidCertificates=true")

# Specify CA file
health.mongodb_check("mongodb://host/db?ssl=true&tlsCAFile=/path/to/ca.pem")
```

## Docker Example

### Docker Compose

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: rootpassword
      MONGO_INITDB_DATABASE: mydb
    volumes:
      - mongo-data:/data/db

volumes:
  mongo-data:
```

### Python Health Check

```python
health.mongodb_check(
    "mongodb://root:rootpassword@localhost:27017/mydb?authSource=admin"
)
```

## Advanced: Custom MongoDB Check

For more detailed MongoDB health information:

```python
from healthcheckx import Health, CheckResult, HealthStatus
from pymongo import MongoClient

def detailed_mongodb_check():
    """Check MongoDB with server status"""
    try:
        client = MongoClient(
            "mongodb://localhost:27017",
            serverSelectionTimeoutMS=3000
        )
        
        # Get server status
        status = client.admin.command("serverStatus")
        
        # Check connections
        current_connections = status['connections']['current']
        available_connections = status['connections']['available']
        
        client.close()
        
        # Determine health
        if available_connections < 10:
            return CheckResult(
                "mongodb-detailed",
                HealthStatus.degraded,
                f"Low available connections: {available_connections}"
            )
        else:
            return CheckResult(
                "mongodb-detailed",
                HealthStatus.healthy,
                f"Connections: {current_connections}/{current_connections + available_connections}"
            )
    except Exception as e:
        return CheckResult(
            "mongodb-detailed",
            HealthStatus.unhealthy,
            str(e)
        )

health = Health()
health.register(detailed_mongodb_check)
health.mongodb_check("mongodb://localhost:27017")

results = health.run()
```

## Performance Monitoring

Track MongoDB health check duration:

```python
from healthcheckx import Health
import time

health = Health()
health.mongodb_check("mongodb://localhost:27017")

# Run multiple times to get average
durations = []
for _ in range(5):
    results = health.run()
    durations.append(results[0].duration_ms)
    time.sleep(1)

avg_duration = sum(durations) / len(durations)
print(f"Average MongoDB health check duration: {avg_duration:.2f}ms")
```

## Next Steps

- [Framework Integration](../frameworks/fastapi.md) - Integrate with web frameworks
- [Custom Checks](../advanced/custom-checks.md) - Create advanced custom checks
- [Multiple Instances](../advanced/multiple-instances.md) - Monitor multiple MongoDB clusters

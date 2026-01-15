# Relational Databases

Health checks for relational database systems including PostgreSQL, MySQL, SQLite, Oracle, and MS SQL Server.

## PostgreSQL

### Basic Usage

```python
from healthcheckx import Health

health = Health()
health.postgresql_check("postgresql://user:password@localhost:5432/mydb")

results = health.run()
```

### Connection Formats

```python
# URL format
health.postgresql_check("postgresql://localhost/mydb")

# With credentials (URL format)
health.postgresql_check("postgresql://user:pass@localhost:5432/mydb")

# Key-value format
health.postgresql_check("host=localhost port=5432 dbname=mydb user=postgres password=secret")

# Key-value with schema
health.postgresql_check("host=localhost dbname=mydb user=app options=-csearch_path=myschema")

# Unix socket
health.postgresql_check("postgresql:///mydb?host=/var/run/postgresql")

# Key-value with Unix socket
health.postgresql_check("host=/var/run/postgresql dbname=mydb")
```

### Multiple Connection Format Examples

```python
# URL format - recommended for simple connections
health.postgresql_check(
    "postgresql://user:password@db.example.com:5432/production",
    name="postgres-prod"
)

# Key-value format - recommended for complex configurations
health.postgresql_check(
    "host=db.example.com port=5432 dbname=production user=app password=secret sslmode=require",
    name="postgres-prod-ssl"
)
```

### Installation

```bash
pip install healthcheckx[postgresql]
```

---

## MySQL

### Basic Usage

```python
health.mysql_check("mysql://root:password@localhost:3306/mydb")
```

### Connection Formats

```python
# Basic
health.mysql_check("mysql://localhost:3306/mydb")

# With credentials
health.mysql_check("mysql://user:pass@localhost:3306/mydb")

# Custom charset
health.mysql_check("mysql://user:pass@localhost:3306/mydb?charset=utf8mb4")
```

### Multiple Databases

```python
health.mysql_check("mysql://user:pass@localhost:3306/users", name="mysql-users")
health.mysql_check("mysql://user:pass@localhost:3306/orders", name="mysql-orders")
```

### Installation

```bash
pip install healthcheckx[mysql]
```

---

## SQLite

### Basic Usage

```python
# File-based database
health.sqlite_check("/path/to/database.db")

# In-memory database
health.sqlite_check(":memory:")
```

### Complete Example

```python
import os
from healthcheckx import Health

health = Health()

# Production database
db_path = os.path.join(os.getcwd(), "data", "production.db")
health.sqlite_check(db_path, name="sqlite-prod")

# Cache database
cache_db = os.path.join(os.getcwd(), "cache.db")
health.sqlite_check(cache_db, timeout=1, name="sqlite-cache")

results = health.run()
```

### Installation

No extra dependencies needed - SQLite is included with Python!

---

## Oracle

### Basic Usage

```python
# URL format
health.oracle_check("oracle://user:password@localhost:1521/XEPDB1")

# TNS format
health.oracle_check("user/password@localhost:1521/service_name")
```

### Connection Formats

```python
# URL format
health.oracle_check("oracle://scott:tiger@localhost:1521/XEPDB1")

# With TNS alias
health.oracle_check("scott/tiger@MYDB")

# Full TNS string
health.oracle_check("system/password@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=XEPDB1)))")
```

### Installation

```bash
pip install healthcheckx[oracle]
```

---

## MS SQL Server

### Basic Usage

```python
health.mssql_check("mssql://sa:Password@localhost:1433/master")
```

### Connection Formats

```python
# Basic
health.mssql_check("mssql://localhost:1433/mydb")

# With credentials
health.mssql_check("mssql://user:pass@localhost:1433/mydb")

# Named instance
health.mssql_check("mssql://user:pass@localhost\\SQLEXPRESS:1433/mydb")

# Windows Authentication (not supported via DSN, use custom check)
```

### Installation

```bash
pip install healthcheckx[mssql]
```

---

## Comparison Table

| Database | Default Port | Connection String | Check Method |
|----------|-------------|------------------|--------------|
| PostgreSQL | 5432 | `postgresql://user:pass@host/db` | SELECT 1 |
| MySQL | 3306 | `mysql://user:pass@host/db` | SELECT 1 |
| SQLite | N/A | `/path/to/db.db` | SELECT 1 |
| Oracle | 1521 | `oracle://user:pass@host/service` | SELECT 1 FROM DUAL |
| MS SQL | 1433 | `mssql://user:pass@host/db` | SELECT 1 |

---

## Complete Multi-Database Example

```python
from healthcheckx import Health, overall_status
import os

health = Health()

# PostgreSQL - Main application database
health.postgresql_check(
    os.getenv("DATABASE_URL", "postgresql://localhost/myapp"),
    timeout=3,
    name="postgres-main"
)

# MySQL - Analytics database
health.mysql_check(
    os.getenv("MYSQL_URL", "mysql://localhost:3306/analytics"),
    timeout=3,
    name="mysql-analytics"
)

# SQLite - Local cache
health.sqlite_check(
    "./cache.db",
    timeout=1,
    name="sqlite-cache"
)

# Run all checks
results = health.run()
status = overall_status(results)

# Report
print(f"Overall Database Health: {status}\n")
for result in results:
    print(f"  {result.name}: {result.status} ({result.duration_ms:.2f}ms)")
```

---

## Best Practices

### 1. Use Connection Pooling

```python
# Health checks create new connections each time
# For production, ensure your app uses connection pooling
```

### 2. Read-Only Checks

```python
# Health checks only run SELECT queries
# No data modification occurs
```

### 3. Set Appropriate Timeouts

```python
# Local databases
health.postgresql_check("postgresql://localhost/db", timeout=2)

# Remote databases
health.postgresql_check("postgresql://remote-db/db", timeout=5)
```

### 4. Monitor Replicas

```python
# Check both primary and replica
health.postgresql_check("postgresql://primary/db", name="db-primary")
health.postgresql_check("postgresql://replica/db", name="db-replica")
```

### 5. Use Environment Variables

```python
import os

db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgresql"):
        health.postgresql_check(db_url)
    elif db_url.startswith("mysql"):
        health.mysql_check(db_url)
```

---

## Common Issues

### Connection Refused

```
Error: Connection refused
```

**Solutions:**
- Verify database is running
- Check host and port
- Verify firewall rules

### Authentication Failed

```
Error: Authentication failed for user
```

**Solutions:**
- Verify username and password
- Check user permissions
- Verify host-based authentication (PostgreSQL pg_hba.conf)

### Database Does Not Exist

```
Error: database "mydb" does not exist
```

**Solutions:**
- Create the database
- Verify database name spelling
- Check if using correct database instance

### SSL/TLS Errors

```
Error: SSL connection required
```

**Solutions for PostgreSQL:**
```python
health.postgresql_check("postgresql://user:pass@host/db?sslmode=require")
```

**Solutions for MySQL:**
```python
health.mysql_check("mysql://user:pass@host/db?ssl=true")
```

---

## Docker Examples

### PostgreSQL

```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"
```

```python
health.postgresql_check("postgresql://postgres:mypassword@localhost:5432/mydb")
```

### MySQL

```yaml
services:
  mysql:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: mydb
    ports:
      - "3306:3306"
```

```python
health.mysql_check("mysql://root:rootpass@localhost:3306/mydb")
```

---

## Next Steps

- [NoSQL Database Checks](nosql.md) - MongoDB and other NoSQL checks
- [Custom Checks](../advanced/custom-checks.md) - Create custom database checks
- [Multiple Instances](../advanced/multiple-instances.md) - Advanced multi-instance monitoring

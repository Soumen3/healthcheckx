# Installation

## Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Basic Installation

Install the core library without any optional dependencies:

```bash
pip install healthcheckx
```

This provides the core functionality and allows you to create custom health checks, but does not include drivers for specific services.

## Installing with Service Support

healthcheckx uses optional dependencies to keep the core library lightweight. Install only the services you need:

### Cache Systems

```bash
# Redis (also works for KeyDB)
pip install healthcheckx[redis]

# Memcached
pip install healthcheckx[memcached]
```

### Message Queues

```bash
# RabbitMQ
pip install healthcheckx[rabbitmq]
```

### Relational Databases

```bash
# PostgreSQL
pip install healthcheckx[postgresql]

# MySQL
pip install healthcheckx[mysql]

# SQLite (no extra dependencies needed - included in Python)

# Oracle
pip install healthcheckx[oracle]

# MS SQL Server
pip install healthcheckx[mssql]
```

### NoSQL Databases

```bash
# MongoDB
pip install healthcheckx[mongodb]
```

## Install Multiple Services

You can install multiple services at once:

```bash
pip install healthcheckx[redis,postgresql,mongodb]
```

## Install All Services

To install all available service drivers:

```bash
pip install healthcheckx[all]
```

This includes:
- Redis (redis>=5.0)
- Memcached (pymemcache>=4.0)
- RabbitMQ (pika>=1.3)
- PostgreSQL (psycopg2-binary>=2.9)
- MySQL (mysql-connector-python>=8.0)
- Oracle (oracledb>=3.4)
- MS SQL Server (pymssql>=2.2)
- MongoDB (pymongo>=4.0)

## Virtual Environment (Recommended)

It's recommended to install healthcheckx in a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/Mac
source venv/bin/activate

# Install healthcheckx
pip install healthcheckx[all]
```

## Verify Installation

After installation, verify that healthcheckx is properly installed:

```python
import healthcheckx
print(healthcheckx.__version__)
```

Or try a simple health check:

```python
from healthcheckx import Health, CheckResult, HealthStatus

health = Health()
print("healthcheckx installed successfully!")
```

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade healthcheckx
```

To upgrade with specific extras:

```bash
pip install --upgrade healthcheckx[all]
```

## Development Installation

If you want to contribute to healthcheckx, clone the repository and install in editable mode:

```bash
# Clone repository
git clone https://github.com/Soumen3/healthcheckx.git
cd healthcheckx

# Install in editable mode with all dependencies
pip install -e .[all]
```

## Troubleshooting

### Import Errors

If you get import errors for specific services:

```python
ModuleNotFoundError: No module named 'redis'
```

Install the required optional dependency:

```bash
pip install healthcheckx[redis]
```

### Version Conflicts

If you experience dependency conflicts, try creating a fresh virtual environment:

```bash
python -m venv fresh_venv
source fresh_venv/bin/activate  # or fresh_venv\Scripts\activate on Windows
pip install healthcheckx[all]
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Get started with healthcheckx
- [Built-in Checks](checks/cache.md) - Explore available health checks
- [Framework Integration](frameworks/fastapi.md) - Integrate with your framework

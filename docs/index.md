# healthcheckx

**Production-grade health checks for Python applications**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/healthcheckx)](https://pypi.org/project/healthcheckx/)

## Overview

healthcheckx is a comprehensive health check library designed for production Python applications. It provides a simple, extensible framework for monitoring the health of various services and components in your application.

## Key Features

- **🔌 Framework Agnostic** - Core library works independently, with optional adapters for FastAPI, Flask, and Django
- **🎯 Built-in Health Checks** - Pre-built checks for popular services:
  - Cache: Redis, KeyDB, Memcached
  - Message Queues: RabbitMQ
  - Relational Databases: PostgreSQL, MySQL, SQLite, Oracle, MS SQL Server
  - NoSQL Databases: MongoDB
- **⚡ Simple & Extensible** - Easy to add custom health checks with a clean API
- **🏷️ Named Checks** - Support for multiple instances of the same service with custom names
- **🎭 Graceful Degradation** - Distinguishes between healthy, degraded, and unhealthy states
- **⏱️ Performance Tracking** - Measures execution time for each health check
- **🛡️ Error Handling** - Catches exceptions gracefully and returns meaningful status
- **🔧 Configurable Timeouts** - Non-blocking checks with configurable timeouts
- **📦 Optional Dependencies** - Install only what you need

## Quick Example

```python
from healthcheckx import Health

# Create health check instance
health = Health()

# Register checks (method chaining supported)
health.redis_check("redis://localhost:6379") \
      .postgresql_check("postgresql://user:pass@localhost/db") \
      .mongodb_check("mongodb://localhost:27017")

# Run all checks
results = health.run()

# Inspect results
for result in results:
    print(f"{result.name}: {result.status} ({result.duration_ms:.2f}ms)")
```

## Installation

```bash
# Basic installation
pip install healthcheckx

# With specific service support
pip install healthcheckx[redis]
pip install healthcheckx[postgresql]

# Install all supported services
pip install healthcheckx[all]
```

## Health Status Levels

healthcheckx supports three levels of health status:

- **`healthy`** - Service is functioning normally
- **`degraded`** - Service is operational but impaired
- **`unhealthy`** - Service is down or failing

## Next Steps

- [Installation Guide](installation.md) - Detailed installation instructions
- [Quick Start](quickstart.md) - Get started in minutes
- [Built-in Checks](checks/cache.md) - Explore available health checks
- [Framework Integration](frameworks/fastapi.md) - Integrate with your framework
- [Custom Checks](advanced/custom-checks.md) - Create your own health checks
- [API Reference](api-reference.md) - Complete API documentation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Author

**Soumen Samanta**

- GitHub: [@Soumen3](https://github.com/Soumen3)
- Repository: [healthcheckx](https://github.com/Soumen3/healthcheckx)

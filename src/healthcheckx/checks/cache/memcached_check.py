from pymemcache.client.base import Client
from pymemcache.exceptions import MemcacheError
from healthcheckx.result import CheckResult, HealthStatus

def create_memcached_check(host: str = "localhost", port: int = 11211, timeout: int = 2, name: str = "memcached"):
    """
    Create a Memcached health check.
    
    Args:
        host: Memcached server host
        port: Memcached server port
        timeout: Connection timeout in seconds
        name: Name for this health check
    
    Returns:
        A health check function that returns CheckResult
    """
    def check():
        try:
            # Create Memcached client
            client = Client(
                (host, port),
                connect_timeout=timeout,
                timeout=timeout
            )
            
            # Test connection with stats command
            stats = client.stats()
            
            # Close the connection
            client.close()
            
            if stats:
                return CheckResult(name, HealthStatus.healthy)
            else:
                return CheckResult(
                    name,
                    HealthStatus.unhealthy,
                    "Failed to retrieve stats"
                )
        except MemcacheError as e:
            return CheckResult(
                name,
                HealthStatus.unhealthy,
                f"Memcache error: {str(e)}"
            )
        except Exception as e:
            return CheckResult(
                name,
                HealthStatus.unhealthy,
                str(e)
            )

    return check

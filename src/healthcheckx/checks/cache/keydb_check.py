import redis
from healthcheckx.result import CheckResult, HealthStatus

def create_keydb_check(keydb_url: str, timeout: int = 2, name: str = "keydb"):
    """
    Create a KeyDB health check.
    
    KeyDB is a Redis-compatible in-memory database, so we use the redis library.
    
    Args:
        keydb_url: KeyDB connection URL (e.g., "redis://localhost:6379" or "keydb://localhost:6379")
        timeout: Connection timeout in seconds
        name: Name for this health check
    
    Returns:
        A health check function that returns CheckResult
    """
    # KeyDB is Redis-compatible, so we can use the redis library
    # Replace keydb:// scheme with redis:// if present
    if keydb_url.startswith("keydb://"):
        keydb_url = keydb_url.replace("keydb://", "redis://", 1)
    
    client = redis.Redis.from_url(keydb_url, socket_timeout=timeout)

    def check():
        try:
            client.ping()
            return CheckResult(
                name=name,
                status=HealthStatus.healthy,
                message="KeyDB is healthy"
            )
        except Exception as e:
            return CheckResult(
                name=name,
                status=HealthStatus.unhealthy,
                error=str(e)
            )

    return check

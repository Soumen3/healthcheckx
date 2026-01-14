import pymssql
from urllib.parse import urlparse
from healthcheckx.result import CheckResult, HealthStatus

def create_mssql_check(dsn: str, timeout: int = 3, name: str = "mssql"):
    """
    Create a MS SQL Server health check.
    
    Args:
        dsn: MS SQL Server connection string (e.g., "mssql://user:password@host:port/database")
        timeout: Connection timeout in seconds
    
    Returns:
        A health check function that returns CheckResult
    """
    def check():
        try:
            # Parse the DSN
            parsed = urlparse(dsn)
            
            conn = pymssql.connect(
                server=parsed.hostname or "localhost",
                port=parsed.port or 1433,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path.lstrip("/") if parsed.path else "master",
                timeout=timeout,
                login_timeout=timeout
            )
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
            cur.close()
            conn.close()
            return CheckResult(name, HealthStatus.healthy)
        except Exception as e:
            return CheckResult(
                name,
                HealthStatus.unhealthy,
                str(e)
            )

    return check

import mysql.connector
from urllib.parse import urlparse
from healthcheckx.result import CheckResult, HealthStatus

def create_mysql_check(dsn: str, timeout: int = 3):
    """
    Create a MySQL health check.
    
    Args:
        dsn: MySQL connection string (e.g., "mysql://user:password@host:port/database")
        timeout: Connection timeout in seconds
    
    Returns:
        A health check function that returns CheckResult
    """
    def check():
        try:
            # Parse the DSN
            parsed = urlparse(dsn)
            
            conn = mysql.connector.connect(
                host=parsed.hostname or "localhost",
                port=parsed.port or 3306,
                user=parsed.username or "root",
                password=parsed.password or "",
                database=parsed.path.lstrip("/") if parsed.path else "",
                connect_timeout=timeout
            )
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
            cur.close()
            conn.close()
            return CheckResult("mysql", HealthStatus.healthy)
        except Exception as e:
            return CheckResult(
                "mysql",
                HealthStatus.unhealthy,
                str(e)
            )

    return check

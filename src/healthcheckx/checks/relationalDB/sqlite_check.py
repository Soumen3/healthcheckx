import sqlite3
from healthcheckx.result import CheckResult, HealthStatus

def create_sqlite_check(db_path: str, timeout: int = 3, name: str = "sqlite"):
    """
    Create a SQLite health check.
    
    Args:
        db_path: Path to the SQLite database file (e.g., "/path/to/database.db" or ":memory:")
        timeout: Connection timeout in seconds
    
    Returns:
        A health check function that returns CheckResult
    """
    def check():
        try:
            conn = sqlite3.connect(db_path, timeout=timeout)
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
            cur.close()
            conn.close()
            return CheckResult(name, status=HealthStatus.healthy, message="SQLite is healthy")
        except Exception as e:
            return CheckResult(
                name,
                status=HealthStatus.unhealthy,
                error=str(e)
            )

    return check

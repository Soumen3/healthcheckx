import oracledb
from healthcheckx.result import CheckResult, HealthStatus

def create_oracle_check(dsn: str, timeout: int = 3):
    """
    Create an Oracle health check.
    
    Args:
        dsn: Oracle connection string (e.g., "oracle://user:password@host:port/service_name")
             or TNS connection string
        timeout: Connection timeout in seconds
    
    Returns:
        A health check function that returns CheckResult
    """
    def check():
        try:
            # Parse DSN if it's a URL format
            if dsn.startswith("oracle://"):
                from urllib.parse import urlparse
                parsed = urlparse(dsn)
                
                conn = oracledb.connect(
                    user=parsed.username,
                    password=parsed.password,
                    host=parsed.hostname or "localhost",
                    port=parsed.port or 1521,
                    service_name=parsed.path.lstrip("/") if parsed.path else None,
                    timeout=timeout * 1000  # oracledb uses milliseconds
                )
            else:
                # TNS or direct connection string
                conn = oracledb.connect(
                    dsn,
                    timeout=timeout * 1000
                )
            
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM DUAL")
            cur.fetchone()
            cur.close()
            conn.close()
            return CheckResult("oracle", HealthStatus.healthy)
        except Exception as e:
            return CheckResult(
                "oracle",
                HealthStatus.unhealthy,
                str(e)
            )

    return check

import psycopg2
from healthcheckx.result import CheckResult, HealthStatus

def create_postgresql_check(dsn: str, timeout: int = 3, name: str = "postgresql"):
    def check():
        try:
            conn = psycopg2.connect(dsn, connect_timeout=timeout)
            cur = conn.cursor()
            cur.execute("SELECT 1")
            conn.close()
            return CheckResult(name, status=HealthStatus.healthy, message="PostgreSQL is healthy")
        except Exception as e:
            return CheckResult(
                name,
                status=HealthStatus.unhealthy,
                error=str(e)
            )

    return check

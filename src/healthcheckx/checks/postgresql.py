import psycopg2
from healthcheckx.result import CheckResult, HealthStatus

def create_postgresql_check(dsn: str, timeout: int = 3):
    def check():
        try:
            conn = psycopg2.connect(dsn, connect_timeout=timeout)
            cur = conn.cursor()
            cur.execute("SELECT 1")
            conn.close()
            return CheckResult("postgresql", HealthStatus.healthy)
        except Exception as e:
            return CheckResult(
                "postgresql",
                HealthStatus.unhealthy,
                str(e)
            )

    return check

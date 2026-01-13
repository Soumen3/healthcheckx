import redis
from healthcheckx.result import CheckResult, HealthStatus

def create_redis_check(redis_url: str, timeout: int = 2):
    client = redis.Redis.from_url(redis_url, socket_timeout=timeout)

    def check():
        try:
            client.ping()
            return CheckResult(
                name="redis",
                status=HealthStatus.healthy
            )
        except Exception as e:
            return CheckResult(
                name="redis",
                status=HealthStatus.unhealthy,
                message=str(e)
            )

    return check

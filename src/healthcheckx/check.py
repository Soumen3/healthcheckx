import shutil
from .result import CheckResult, HealthStatus

def disk_check(min_free_percent=10):
    total, used, free = shutil.disk_usage("/")
    free_percent = (free / total) * 100

    status = HealthStatus.healthy if free_percent > min_free_percent else HealthStatus.unhealthy

    return CheckResult(
        name="disk",
        status=status,
        message=f"Free disk: {free_percent:.2f}%"
    )

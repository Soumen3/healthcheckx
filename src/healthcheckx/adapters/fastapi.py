from fastapi import Response
from healthcheckx.core import overall_status

class FastAPIAdapter:
    def __init__(self, health):
        self.health = health

    async def endpoint(self):
        results = self.health.run()
        status = overall_status(results)

        http_status = 200 if status != "unhealthy" else 503

        return {
            "status": status,
            "checks": [r.__dict__ for r in results]
        }, http_status

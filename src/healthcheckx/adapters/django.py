from django.http import JsonResponse
from healthcheckx.core import overall_status

def django_health_view(request, health):
    results = health.run()
    status = overall_status(results)

    return JsonResponse({
        "status": status,
        "checks": [r.__dict__ for r in results]
    }, status=200 if status != "unhealthy" else 503)

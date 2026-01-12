from flask import jsonify
from healthcheckx.core import overall_status

def flask_health_endpoint(health):
    results = health.run()
    status = overall_status(results)

    return jsonify({
        "status": status,
        "checks": [r.__dict__ for r in results]
    }), 200 if status != "unhealthy" else 503

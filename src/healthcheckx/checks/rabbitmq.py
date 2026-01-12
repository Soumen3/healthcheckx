import pika
from healthcheckx.result import CheckResult, HealthStatus

def create_rabbitmq_check(amqp_url: str, timeout: int = 2):
    params = pika.URLParameters(amqp_url)
    params.socket_timeout = timeout

    def check():
        try:
            conn = pika.BlockingConnection(params)
            conn.close()
            return CheckResult("rabbitmq", HealthStatus.healthy)
        except Exception as e:
            return CheckResult(
                "rabbitmq",
                HealthStatus.unhealthy,
                str(e)
            )

    return check

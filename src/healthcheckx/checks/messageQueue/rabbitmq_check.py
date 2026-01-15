import pika
from healthcheckx.result import CheckResult, HealthStatus

def create_rabbitmq_check(amqp_url: str, timeout: int = 2, name: str = "rabbitmq"):
    params = pika.URLParameters(amqp_url)
    params.socket_timeout = timeout

    def check():
        try:
            conn = pika.BlockingConnection(params)
            conn.close()
            return CheckResult(name, HealthStatus.healthy, message="RabbitMQ is healthy")
        except Exception as e:
            return CheckResult(
                name,
                HealthStatus.unhealthy,
                error=str(e)
            )

    return check

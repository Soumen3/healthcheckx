from __future__ import annotations
from typing import Optional
from healthcheckx.result import CheckResult, HealthStatus


def create_kafka_check(bootstrap_servers: str, timeout: int = 2, name: str = "kafka"):
    """
    Create a Kafka health check function.
    
    Args:
        bootstrap_servers: Comma-separated list of Kafka broker addresses (e.g., "localhost:9092" or "broker1:9092,broker2:9092")
        timeout: Connection timeout in seconds (default: 2)
        name: Name for this health check (default: "kafka")
    
    Returns:
        A function that performs the health check
    
    Example:
        >>> from healthcheckx import Health
        >>> health = Health()
        >>> health.kafka_check("localhost:9092", name="kafka-broker")
    """
    def check():
        try:
            from kafka import KafkaAdminClient
            from kafka.errors import KafkaError
            
            # Convert bootstrap_servers string to list
            servers = [s.strip() for s in bootstrap_servers.split(',')]
            
            # Create admin client to check connection
            admin_client = KafkaAdminClient(
                bootstrap_servers=servers,
                request_timeout_ms=timeout * 1000,
                api_version_auto_timeout_ms=timeout * 1000,
                connections_max_idle_ms=timeout * 1000
            )
            
            # Try to get cluster metadata to verify connection
            admin_client.list_topics()
            
            # Close the connection
            admin_client.close()
            
            return CheckResult(name, HealthStatus.healthy)
            
        except ImportError:
            return CheckResult(
                name,
                HealthStatus.unhealthy,
                "kafka-python package not installed. Install with: pip install kafka-python"
            )
        except KafkaError as e:
            return CheckResult(
                name,
                HealthStatus.unhealthy,
                f"Kafka error: {str(e)}"
            )
        except Exception as e:
            return CheckResult(
                name,
                HealthStatus.unhealthy,
                str(e)
            )
    
    return check

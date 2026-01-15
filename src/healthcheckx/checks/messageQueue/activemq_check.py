from __future__ import annotations
from typing import Optional
from healthcheckx.result import CheckResult, HealthStatus
import socket


def create_activemq_check(broker_url: str, timeout: int = 2, name: str = "activemq"):
    """
    Create an ActiveMQ health check function.
    
    Args:
        broker_url: ActiveMQ broker URL 
                   - For OpenWire/TCP: "tcp://localhost:61616" or "localhost:61616"
                   - For STOMP: "stomp://localhost:61613"
        timeout: Connection timeout in seconds (default: 2)
        name: Name for this health check (default: "activemq")
    
    Returns:
        A function that performs the health check
    
    Example:
        >>> from healthcheckx import Health
        >>> health = Health()
        >>> # TCP/OpenWire protocol (port 61616)
        >>> health.activemq_check("tcp://localhost:61616", name="activemq-tcp")
        >>> # STOMP protocol (port 61613)
        >>> health.activemq_check("stomp://localhost:61613", name="activemq-stomp")
    """
    def check():
        # Parse broker URL
        if broker_url.startswith("stomp://"):
            protocol = "stomp"
            host_port = broker_url.replace("stomp://", "")
        elif broker_url.startswith("tcp://"):
            protocol = "tcp"
            host_port = broker_url.replace("tcp://", "")
        else:
            # Try to detect protocol by port, default to TCP
            host_port = broker_url
            # Check if port suggests STOMP (61613)
            if ":61613" in host_port or host_port.endswith("61613"):
                protocol = "stomp"
            else:
                protocol = "tcp"
        
        # Parse host and port
        if ":" in host_port:
            host, port_str = host_port.split(":", 1)
            port = int(port_str.split("/")[0])  # Remove any trailing path
        else:
            host = host_port.split("/")[0]
            # Default ports
            port = 61613 if protocol == "stomp" else 61616
        
        # Use appropriate connection method based on protocol
        if protocol == "stomp":
            return _check_stomp_connection(host, port, timeout, name)
        else:
            return _check_tcp_connection(host, port, timeout, name)
    
    return check


def _check_stomp_connection(host: str, port: int, timeout: int, name: str) -> CheckResult:
    """Check ActiveMQ using STOMP protocol"""
    try:
        import stomp
        from stomp.exception import ConnectFailedException
        
        conn = stomp.Connection([(host, port)])
        conn.set_listener('', stomp.PrintingListener())
        
        # Try to connect
        conn.connect(wait=True, timeout=timeout)
        
        # If connection successful, disconnect and return healthy
        if conn.is_connected():
            conn.disconnect()
            return CheckResult(name, HealthStatus.healthy)
        else:
            return CheckResult(
                name,
                HealthStatus.unhealthy,
                "Failed to establish STOMP connection"
            )
        
    except ImportError:
        return CheckResult(
            name,
            HealthStatus.unhealthy,
            "stomp.py package not installed. Install with: pip install stomp.py"
        )
    except ConnectFailedException as e:
        return CheckResult(
            name,
            HealthStatus.unhealthy,
            f"STOMP connection failed: {str(e)}"
        )
    except Exception as e:
        return CheckResult(
            name,
            HealthStatus.unhealthy,
            f"STOMP error: {str(e)}"
        )


def _check_tcp_connection(host: str, port: int, timeout: int, name: str) -> CheckResult:
    """Check ActiveMQ using TCP socket connection (OpenWire protocol)"""
    try:
        # Create a socket connection to check if the port is accessible
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Try to connect
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return CheckResult(name, HealthStatus.healthy)
        else:
            return CheckResult(
                name,
                HealthStatus.unhealthy,
                f"TCP connection failed to {host}:{port}"
            )
        
    except socket.timeout:
        return CheckResult(
            name,
            HealthStatus.unhealthy,
            f"Connection timeout to {host}:{port}"
        )
    except socket.gaierror as e:
        return CheckResult(
            name,
            HealthStatus.unhealthy,
            f"DNS resolution failed: {str(e)}"
        )
    except Exception as e:
        return CheckResult(
            name,
            HealthStatus.unhealthy,
            f"TCP connection error: {str(e)}"
        )

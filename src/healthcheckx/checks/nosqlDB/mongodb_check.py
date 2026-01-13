from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from healthcheckx.result import CheckResult, HealthStatus

def create_mongodb_check(connection_string: str, timeout: int = 3):
    """
    Create a MongoDB health check.
    
    Args:
        connection_string: MongoDB connection string (e.g., "mongodb://localhost:27017" or 
                          "mongodb://user:password@host:27017/database")
        timeout: Connection timeout in seconds
    
    Returns:
        A health check function that returns CheckResult
    """
    def check():
        try:
            # Create MongoDB client with timeout
            client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=timeout * 1000,
                connectTimeoutMS=timeout * 1000
            )
            
            # Ping the server to verify connection
            client.admin.command('ping')
            
            # Close the connection
            client.close()
            
            return CheckResult("mongodb", HealthStatus.healthy)
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            return CheckResult(
                "mongodb",
                HealthStatus.unhealthy,
                f"Connection failed: {str(e)}"
            )
        except Exception as e:
            return CheckResult(
                "mongodb",
                HealthStatus.unhealthy,
                str(e)
            )

    return check

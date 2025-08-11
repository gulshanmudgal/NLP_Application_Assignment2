#!/usr/bin/env python3
"""
Health check script for the NLP Translation backend service.
Used by Docker health checks and monitoring systems.
"""
import sys
import requests
import json
from typing import Dict, Any

def check_health() -> Dict[str, Any]:
    """
    Perform comprehensive health check of the backend service.
    
    Returns:
        Dict containing health check results
    """
    results = {
        "status": "healthy",
        "checks": {},
        "timestamp": None
    }
    
    try:
        # Check main health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            results["checks"]["health_endpoint"] = {
                "status": "pass",
                "response_time": response.elapsed.total_seconds(),
                "data": health_data
            }
            results["timestamp"] = health_data.get("timestamp")
        else:
            results["checks"]["health_endpoint"] = {
                "status": "fail",
                "error": f"HTTP {response.status_code}"
            }
            results["status"] = "unhealthy"
            
    except requests.exceptions.ConnectionError:
        results["checks"]["health_endpoint"] = {
            "status": "fail",
            "error": "Connection refused"
        }
        results["status"] = "unhealthy"
        
    except requests.exceptions.Timeout:
        results["checks"]["health_endpoint"] = {
            "status": "fail",
            "error": "Request timeout"
        }
        results["status"] = "unhealthy"
        
    except Exception as e:
        results["checks"]["health_endpoint"] = {
            "status": "fail",
            "error": str(e)
        }
        results["status"] = "unhealthy"
    
    # Check if we can reach the API endpoints
    try:
        response = requests.get("http://localhost:8000/api/v1/languages/", timeout=5)
        if response.status_code == 200:
            results["checks"]["api_endpoints"] = {
                "status": "pass",
                "response_time": response.elapsed.total_seconds()
            }
        else:
            results["checks"]["api_endpoints"] = {
                "status": "fail",
                "error": f"HTTP {response.status_code}"
            }
            results["status"] = "degraded"
            
    except Exception as e:
        results["checks"]["api_endpoints"] = {
            "status": "fail",
            "error": str(e)
        }
        results["status"] = "degraded"
    
    return results

def main():
    """Main health check function."""
    try:
        health_results = check_health()
        
        # Print results as JSON
        print(json.dumps(health_results, indent=2))
        
        # Exit with appropriate code
        if health_results["status"] == "healthy":
            sys.exit(0)
        elif health_results["status"] == "degraded":
            sys.exit(1)
        else:
            sys.exit(2)
            
    except Exception as e:
        print(json.dumps({
            "status": "unhealthy",
            "error": str(e)
        }))
        sys.exit(2)

if __name__ == "__main__":
    main()

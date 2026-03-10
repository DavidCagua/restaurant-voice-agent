"""
Health check endpoint for the agent server.

Lightweight health check that verifies required environment variables
and checks connectivity to dependencies.
"""

import os
import requests
from typing import Dict, Tuple
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from dotenv import load_dotenv

load_dotenv()

# Required environment variables
REQUIRED_ENV_VARS = [
    "LIVEKIT_URL",
    "LIVEKIT_API_KEY",
    "LIVEKIT_API_SECRET",
    "OPENAI_API_KEY",
    "ELEVENLABS_API_KEY",
    "DEEPGRAM_API_KEY",
]

# API base URL for connectivity check
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3000/v1")


def check_env_vars() -> Tuple[bool, Dict[str, str]]:
    """
    Check if all required environment variables are present.
    
    Returns:
        Tuple of (all_present, missing_vars_dict)
    """
    missing = {}
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing[var] = "missing"
    
    return len(missing) == 0, missing


def check_api_connectivity(timeout: float = 2.0) -> Tuple[bool, str]:
    """
    Check if the backend API is reachable.
    
    Args:
        timeout: Request timeout in seconds
    
    Returns:
        Tuple of (is_reachable, status_message)
    """
    try:
        # Try to reach the API base URL (without specific endpoint to avoid auth)
        response = requests.get(API_BASE_URL.replace("/v1", ""), timeout=timeout)
        return True, f"API reachable (status: {response.status_code})"
    except requests.exceptions.ConnectionError:
        return False, "API not reachable (connection error)"
    except requests.exceptions.Timeout:
        return False, "API not reachable (timeout)"
    except Exception as e:
        return False, f"API check failed: {str(e)}"


def get_health_status() -> Tuple[int, Dict]:
    """
    Get overall health status of the agent server.
    
    Returns:
        Tuple of (http_status_code, health_status_dict)
    """
    env_ok, missing_env = check_env_vars()
    api_ok, api_status = check_api_connectivity()
    
    healthy = env_ok and api_ok
    
    status = {
        "status": "healthy" if healthy else "unhealthy",
        "checks": {
            "environment_variables": {
                "status": "ok" if env_ok else "error",
                "missing": missing_env if not env_ok else []
            },
            "api_connectivity": {
                "status": "ok" if api_ok else "error",
                "message": api_status
            }
        }
    }
    
    http_status = 200 if healthy else 503
    return http_status, status


class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP request handler for health check endpoint."""
    
    def do_GET(self):
        """Handle GET requests to /health."""
        if self.path == "/health" or self.path == "/health/":
            http_status, status = get_health_status()
            
            self.send_response(http_status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            import json
            self.wfile.write(json.dumps(status, indent=2).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging for health checks."""
        pass


def start_health_server(port: int = 8080) -> HTTPServer:
    """
    Start a lightweight HTTP server for health checks.
    
    Args:
        port: Port to listen on
    
    Returns:
        HTTPServer instance
    """
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    
    def run_server():
        server.serve_forever()
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    
    return server


def check_health() -> Dict:
    """
    Simple function to check health without starting a server.
    Useful for programmatic health checks.
    
    Returns:
        Health status dictionary
    """
    _, status = get_health_status()
    return status

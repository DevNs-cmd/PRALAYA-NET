"""
Middleware for rate limiting, input validation, and security
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import time
from collections import defaultdict
from datetime import datetime, timedelta
import re
import json

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware
    Limits requests per IP address
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_times = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Get current time
        now = time.time()
        cutoff = now - 60  # Last 60 seconds
        
        # Clean old requests from this IP
        self.request_times[client_ip] = [
            t for t in self.request_times[client_ip] if t > cutoff
        ]
        
        # Check rate limit
        if len(self.request_times[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute",
                    "retry_after": 60
                }
            )
        
        # Add this request
        self.request_times[client_ip].append(now)
        
        # Continue to next middleware/route
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.request_times[client_ip])
        )
        
        return response


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate request inputs for security and correctness
    """
    
    # Patterns for validation
    VALID_DISASTER_TYPES = ["flood", "fire", "earthquake", "cyclone", "landslide", "test"]
    VALID_SEVERITY_RANGE = (0.0, 1.0)
    VALID_COORDINATES = {
        "lat_range": (-90, 90),
        "lon_range": (-180, 180)
    }
    
    async def dispatch(self, request: Request, call_next):
        # Skip validation for GET requests
        if request.method == "GET":
            response = await call_next(request)
            return response
        
        # Skip validation for multipart/form-data (file uploads)
        content_type = request.headers.get("content-type", "").lower()
        if "multipart/form-data" in content_type:
            response = await call_next(request)
            return response
        
        try:
            # Get body for validation (only for JSON)
            body = await request.body()
            
            if body:
                data = json.loads(body)
                
                # Validate disaster injection endpoints
                if "/trigger" in request.url.path or "/inject" in request.url.path:
                    self._validate_disaster_data(data)
                
                # Validate coordinates if present
                if "location" in data:
                    self._validate_location(data["location"])
            
        except json.JSONDecodeError:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid JSON in request body"}
            )
        except ValueError as e:
            return JSONResponse(
                status_code=400,
                content={"error": str(e)}
            )
        
        # Reconstruct request with body for actual handler
        async def receive():
            return {"type": "http.request", "body": body}
        
        request._receive = receive
        response = await call_next(request)
        return response
    
    @staticmethod
    def _validate_disaster_data(data: dict):
        """Validate disaster injection data"""
        if "disaster_type" in data:
            if data["disaster_type"] not in InputValidationMiddleware.VALID_DISASTER_TYPES:
                raise ValueError(
                    f"Invalid disaster_type. Must be one of: {', '.join(InputValidationMiddleware.VALID_DISASTER_TYPES)}"
                )
        
        if "severity" in data:
            severity = data["severity"]
            min_sev, max_sev = InputValidationMiddleware.VALID_SEVERITY_RANGE
            if not (min_sev <= severity <= max_sev):
                raise ValueError(f"Severity must be between {min_sev} and {max_sev}")
    
    @staticmethod
    def _validate_location(location: dict):
        """Validate GPS coordinates"""
        if isinstance(location, dict):
            if "lat" in location:
                lat = location["lat"]
                lat_min, lat_max = InputValidationMiddleware.VALID_COORDINATES["lat_range"]
                if not (lat_min <= lat <= lat_max):
                    raise ValueError(f"Latitude must be between {lat_min} and {lat_max}")
            
            if "lon" in location:
                lon = location["lon"]
                lon_min, lon_max = InputValidationMiddleware.VALID_COORDINATES["lon_range"]
                if not (lon_min <= lon <= lon_max):
                    raise ValueError(f"Longitude must be between {lon_min} and {lon_max}")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all incoming requests for monitoring
    """
    
    async def dispatch(self, request: Request, call_next):
        # Log request
        start_time = time.time()
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        
        print(f"[{datetime.now().isoformat()}] {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
        
        return response

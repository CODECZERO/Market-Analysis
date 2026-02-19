"""
Security Middleware
- Security headers
- Rate limiting
- Request logging
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import os


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS Protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HTTPS enforcement (production only)
        if os.getenv("ENV") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
        )
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Log request timing for monitoring"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Add request ID for tracking
        request_id = f"{int(start_time * 1000000)}"
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Add timing header
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            
            # Log slow requests
            if duration > 5.0:  # > 5 seconds
                print(f"⚠️  SLOW REQUEST [{request_id}]: {request.method} {request.url.path} took {duration:.2f}s")
            
            return response
            
        except Exception as e:
            # Log error with request ID
            print(f"❌ ERROR [{request_id}]: {request.method} {request.url.path} - {str(e)}")
            raise

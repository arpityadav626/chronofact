# FastAPI Security Middleware
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from .auth import rate_limiter, decode_token

# Security headers middleware
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

# Add security headers
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response

# Rate limiting middleware
async def rate_limit_middleware(request: Request, call_next):
    # Skip auth endpoint
    if request.url.path == "/api/auth/login":
        return await call_next(request)
    
    client_id = request.client.host if request.client else "unknown"
    if not rate_limiter.is_allowed(client_id):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Try again later."}
        )
    
    return await call_next(request)

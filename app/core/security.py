"""HTTP security middleware (registered in app/main.py - previously defined but never attached)."""
from fastapi import Request, status
from fastapi.responses import JSONResponse

from .auth import rate_limiter


async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    h = response.headers
    h["X-Content-Type-Options"] = "nosniff"
    h["X-Frame-Options"] = "DENY"
    h["Referrer-Policy"] = "no-referrer"
    h["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    # Directives that cannot break the current UI (inline scripts + CDN assets still work).
    # Tighten script-src/style-src after vendoring Tailwind/Lucide/fonts locally (see README).
    h["Content-Security-Policy"] = "frame-ancestors 'none'; object-src 'none'; base-uri 'self'; form-action 'self'"
    if request.url.path.startswith("/api/"):
        h["Cache-Control"] = "no-store"
    if request.headers.get("x-forwarded-proto", request.url.scheme) == "https":
        h["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


async def rate_limit_middleware(request: Request, call_next):
    """General per-IP limit on API calls. Login has its own stricter throttle in the endpoint."""
    if request.url.path.startswith("/api/") and request.url.path != "/api/health":
        client_id = request.client.host if request.client else "unknown"
        if not rate_limiter.is_allowed(client_id):
            return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                content={"detail": "Rate limit exceeded. Try again later."})
    return await call_next(request)

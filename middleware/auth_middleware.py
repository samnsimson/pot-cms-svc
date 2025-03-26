from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from config import config
from starlette.middleware.base import BaseHTTPMiddleware
from exceptions import UnauthorizedException
from responses import AuthResponse
from services.auth_service import AuthService
from fnmatch import fnmatch


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, dispatch=None):
        super().__init__(app, dispatch)
        self.exclude_urls = ["/docs", "/api/v1/openapi.json", "/api/v1/auth/*"]
        self.auth_scheme = config.AUTH_SCHEME
        self.auth_service = AuthService()
        self.time_widow = timedelta(minutes=5)

    def is_near_expiry(self, payload: dict):
        expiry_time = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        current_time = datetime.now(timezone.utc)
        return (expiry_time - current_time) <= timedelta(minutes=5)

    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            if any(fnmatch(request.url.path, pattern) for pattern in self.exclude_urls): return response
            token = await self.auth_scheme(request)
            if not token: raise UnauthorizedException("Missing authentication token")
            payload = self.auth_service.verify_token(token)
            return response
        except HTTPException as e: return AuthResponse(str(e))

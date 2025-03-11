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
            if self.is_near_expiry(payload):
                token_data = {"sub": payload.get("sub", None), "host": payload.get("host", None), "role": payload.get("role", None)}
                new_token = self.auth_service.create_access_token(token_data)
                response.set_cookie(key="access_token", value=new_token, max_age=timedelta(minutes=30), httponly=True, secure=True, samesite="lax", path="/")
                return response
            else: response.delete_cookie(key="access_token")
            return response
        except HTTPException as e: return AuthResponse(str(e))

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
        self.exclude_urls = ["/docs", "/api/v1/openapi.json", "/auth/*"]
        self.auth_scheme = config.AUTH_SCHEME
        self.auth_service = AuthService()

    async def dispatch(self, request, call_next):
        try:
            if any(fnmatch(request.url.path, pattern) for pattern in self.exclude_urls): return await call_next(request)
            token = await self.auth_scheme(request)
            if not token: raise UnauthorizedException("Missing authentication token")
            payload = self.auth_service.verify_token(token)
            user_data = {"id": payload.get("sub", None), "host": payload.get("host", None), "role": payload.get("role", None)}
            setattr(request.state, "user", user_data)
            return await call_next(request)
        except HTTPException as e: return AuthResponse(str(e))

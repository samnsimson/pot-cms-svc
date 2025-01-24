from typing import Any
from fastapi.responses import JSONResponse
from starlette import status


class AuthResponse(JSONResponse):
    def __init__(self, detail: str, headers: dict[str, Any] = None):
        super().__init__(content=detail, status_code=status.HTTP_401_UNAUTHORIZED, headers=headers)

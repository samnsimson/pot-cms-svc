from typing import Annotated
from fastapi import Depends, Request
from httpx import AsyncClient
from redis import Redis
from config import config
from jose import JWTError, jwt
from exceptions import UnauthorizedException
from models import MediaTypeEnum
from schemas.utils_schema import CurrentUser


async def get_current_user(token: Annotated[str, Depends(config.AUTH_SCHEME)]):
    try:
        if not token: raise UnauthorizedException("Missing authentication token")
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        user_id = payload.get("sub")
        user_role = payload.get("role")
        domain = payload.get("domain")
        host = payload.get("host")
        if user_id is None: raise UnauthorizedException(detail="Unauthorized")
        return CurrentUser(id=user_id, host=host, domain=domain, role=user_role)
    except JWTError:
        raise UnauthorizedException("Unauthorized, Error validating jwt token")


def get_http_client(request: Request) -> AsyncClient:
    return request.app.state.http_client


def get_media_type(content_type: str) -> MediaTypeEnum:
    if content_type.startswith("image/"):
        return MediaTypeEnum.image
    elif content_type.startswith("video/"):
        return MediaTypeEnum.video
    elif content_type.startswith("audio/"):
        return MediaTypeEnum.audio
    return MediaTypeEnum.other

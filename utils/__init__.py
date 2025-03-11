from typing import Annotated
from fastapi import Depends
from config import config
from jose import JWTError, jwt
from exceptions import UnauthorizedException
from schemas.utils_schema import CurrentUser


async def get_current_user(token: Annotated[str, Depends(config.AUTH_SCHEME)]):
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        user_id = payload.get("sub")
        user_role = payload.get("role")
        domain = payload.get("domain")
        host = payload.get("host")
        if user_id is None: raise UnauthorizedException(detail="Unauthorized")
        return CurrentUser(id=user_id, host=host, domain=domain, role=user_role)
    except JWTError:
        raise UnauthorizedException("Unauthorized, Error validating jwt token")

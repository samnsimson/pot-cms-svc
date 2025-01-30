from fastapi import Request
from exceptions import UnauthorizedException
from schemas.utils_schema import CurrentUser


def get_current_user(request: Request) -> CurrentUser:
    user_data: dict = request.state.__getattr__("user")
    user_id = user_data.get("id", None)
    user_role = user_data.get("role", None)
    host = user_data.get("host", None)
    if (user_id or user_role or host) is None: raise UnauthorizedException("Unauthorized")
    return CurrentUser(id=user_id, host=host, role=user_role)

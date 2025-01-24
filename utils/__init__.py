from fastapi import Request
from schemas.utils_schema import CurrentUser


def get_current_user(request: Request) -> CurrentUser:
    user_data: dict = request.state.__getattr__("user")
    user_id = user_data.get("id", None)
    user_role = user_data.get("role", None)
    host = user_data.get("host", None)
    return CurrentUser(user_id, host, user_role)

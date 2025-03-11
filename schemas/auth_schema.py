from typing import Optional
from sqlmodel import SQLModel

from models import RoleEnum


class AuthResponseSchema(SQLModel):
    status: str
    user_id: str
    host: str
    role: RoleEnum
    redirect_url: Optional[str]
    access_token: str
    refresh_token: str
    token_type: str
    token_max_age: float


class RefreshBody(SQLModel):
    token: str

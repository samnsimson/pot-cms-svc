from typing import Optional
from sqlmodel import Field, SQLModel
from models import RoleEnum


class CurrentUser(SQLModel):
    id: str
    host: str
    domain: str
    role: RoleEnum

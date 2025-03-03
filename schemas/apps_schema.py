from datetime import datetime
from typing import List
from uuid import UUID
from sqlmodel import SQLModel

from models import User
from schemas.base_schema import ID
from schemas.user_schema import UserOutSchema


class AppsSchema(SQLModel):
    name: str


class AppCreateSchema(AppsSchema):
    pass


class AppOutSchema(AppsSchema, ID):
    secret: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    users: List[UserOutSchema]

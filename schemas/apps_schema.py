from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel

from schemas.base_schema import ID


class AppsSchema(SQLModel):
    name: str


class AppCreateSchema(AppsSchema):
    pass


class AppOutSchema(AppsSchema, ID):
    secret: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

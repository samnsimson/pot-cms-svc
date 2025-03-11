from datetime import datetime
from sqlmodel import SQLModel

from schemas.base_schema import ID


class AppsSchema(SQLModel):
    name: str


class AppCreateSchema(AppsSchema):
    pass


class AppOutSchema(AppsSchema, ID):
    slug: str
    secret: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AppDeleteOutSchema(SQLModel, ID):
    status: str

from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel


class AppsSchema(SQLModel):
    name: str


class AppCreateSchema(AppsSchema):
    pass


class AppOutSchema(AppsSchema):
    id: UUID
    secret: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

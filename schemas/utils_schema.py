from uuid import UUID
from sqlmodel import SQLModel
from models import RoleEnum


class CurrentUser(SQLModel):
    id: UUID
    host: UUID
    role: RoleEnum

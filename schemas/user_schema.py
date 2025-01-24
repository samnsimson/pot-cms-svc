from datetime import datetime
from uuid import UUID
from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class UserSchema(SQLModel):
    username: str
    email: EmailStr
    phone: str


class UserCreateSchema(UserSchema):
    password: str = Field(min_length=6, max_length=16)


class UserOutSchema(UserSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime

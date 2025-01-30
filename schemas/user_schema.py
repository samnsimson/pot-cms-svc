from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import EmailStr
from sqlmodel import SQLModel, Field
from models import Role
from schemas.base_schema import ID
from schemas.domain_schema import DomainCreateSchema


class UserSchema(SQLModel):
    username: str
    email: EmailStr
    phone: str


class UserCreateSchema(UserSchema):
    password: str = Field(min_length=6, max_length=16)
    domain: DomainCreateSchema


class UserOutSchema(UserSchema, ID):
    created_at: datetime
    updated_at: datetime

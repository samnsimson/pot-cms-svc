import re
import secrets
from typing import Optional
from uuid import UUID, uuid4
from pydantic import field_validator
from sqlalchemy import text
from sqlmodel import Field, SQLModel
from datetime import datetime, timezone

uuid_kwargs = {"server_default": text("gen_random_uuid()"), "unique": True}
created_at_kwargs = {"server_default": text("current_timestamp(0)")}
updated_at_kwargs = {"server_default": text("current_timestamp(0)"), "onupdate": text("current_timestamp(0)")}


def get_timestamp() -> datetime:
    return datetime.now(timezone.utc)


def generate_secret_key() -> str:
    length: int = 32
    return secrets.token_hex(length)


class BaseModel(SQLModel):
    id: UUID = Field(primary_key=True, index=True, nullable=False, default_factory=uuid4, sa_column_kwargs=uuid_kwargs)


class Timestamp(SQLModel):
    created_at: datetime = Field(default_factory=get_timestamp, nullable=False, sa_column_kwargs=created_at_kwargs)
    updated_at: datetime = Field(default_factory=get_timestamp, nullable=False, sa_column_kwargs=updated_at_kwargs)


class Client(BaseModel, Timestamp, table=True):
    name: Optional[str] = Field(default=None)
    secret: str = Field(default_factory=generate_secret_key, nullable=False)
    is_active: bool = Field(default=True, nullable=False)


class User(BaseModel, Timestamp, table=True):
    username: str = Field(nullable=False, unique=True, index=True, min_length=3)
    email: str = Field(nullable=False, unique=True, index=True)
    phone: str = Field(nullable=False, unique=True, index=True)
    password: str = Field(nullable=False)

    @field_validator('email')
    def validate_email(cls, value: str) -> str:
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value): raise ValueError("Invalid email format")
        return value

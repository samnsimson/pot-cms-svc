import re
import secrets
from typing import Optional
from uuid import uuid4
from pydantic import field_validator
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel
from datetime import datetime, timezone


def generate_uuid():
    return str(uuid4())


def generate_secret_key() -> str:
    length: int = 32
    return secrets.token_hex(length)


class TimeStamp:
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class Client(SQLModel, TimeStamp, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, nullable=False)
    name: Optional[str] = Field(default=None)
    secret: str = Field(default_factory=generate_secret_key, nullable=False)
    is_active: bool = Field(default=True, nullable=False)


class User(SQLModel, TimeStamp, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, nullable=False)
    username: str = Field(nullable=False, unique=True, index=True, min_length=3)
    email: str = Field(nullable=False, unique=True, index=True)
    phone: str = Field(nullable=False, unique=True, index=True)
    password: str = Field(nullable=False)

    @field_validator('email')
    def validate_email(cls, value: str) -> str:
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value): raise ValueError("Invalid email format")
        return value

from enum import Enum
import secrets
from typing import List, Optional
from uuid import uuid4
from pydantic import Json
from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel, JSON
from datetime import datetime, timezone

#################### HELPERS ####################


def generate_uuid():
    return str(uuid4())


def generate_secret_key() -> str:
    length: int = 32
    return secrets.token_hex(length)

#################### ENUMS ####################


class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"
    super_admin = "super_admin"

#################### MIXINS ####################


class TimeStamp:
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

#################### MANY TO MANY MODELS ####################


class UserApps(SQLModel, TimeStamp, table=True):
    user_id: str = Field(foreign_key="user.id", primary_key=True, ondelete="CASCADE")
    app_id: str = Field(foreign_key="app.id", primary_key=True, ondelete="CASCADE")


class RolePermission(SQLModel, TimeStamp, table=True):
    role_id: str = Field(foreign_key="role.id", primary_key=True)
    permission_id: str = Field(foreign_key="permission.id", primary_key=True)

#################### MODELS ####################


class Role(SQLModel, TimeStamp, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, nullable=False)
    name: RoleEnum = Field(nullable=False, unique=True, index=True)
    users: List["User"] = Relationship(back_populates="role")
    permissions: List["Permission"] = Relationship(back_populates="roles", link_model=RolePermission)


class Permission(SQLModel, TimeStamp, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, nullable=False)
    name: str = Field(nullable=False, unique=True)
    description: Optional[str] = Field(default=None)
    roles: List["Role"] = Relationship(back_populates="permissions", link_model=RolePermission)


class Domain(SQLModel, TimeStamp, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, nullable=False)
    name: str = Field(nullable=False)
    host: str = Field(nullable=False, unique=True, index=True)
    url: Optional[str] = Field(default=None, nullable=True, unique=True, index=True)
    is_active: bool = Field(default=True, nullable=False)
    users: List["User"] = Relationship(back_populates="domain", cascade_delete=True)
    apps: List["App"] = Relationship(back_populates="domain", cascade_delete=True)


class App(SQLModel, TimeStamp, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, nullable=False)
    name: Optional[str] = Field(default=None)
    secret: str = Field(default_factory=generate_secret_key, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    domain_id: str = Field(foreign_key="domain.id", ondelete="CASCADE")
    domain: Domain = Relationship(back_populates="apps")
    users: List["User"] = Relationship(back_populates="apps", link_model=UserApps)
    content: List["Content"] = Relationship(back_populates="app", cascade_delete=True)


class User(SQLModel, TimeStamp, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, nullable=False)
    username: str = Field(nullable=False, unique=True, index=True, min_length=3)
    email: str = Field(nullable=False, unique=True, index=True)
    phone: str = Field(nullable=False, unique=True, index=True)
    password: str = Field(nullable=False)
    domain_id: Optional[str] = Field(default=None, foreign_key="domain.id", nullable=True, ondelete="CASCADE")
    role_id: str = Field(foreign_key="role.id")
    domain: Optional[Domain] = Relationship(back_populates="users")
    role: Role = Relationship(back_populates="users")
    apps: List["App"] = Relationship(back_populates="users", link_model=UserApps)


class Content(SQLModel, TimeStamp, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, nullable=False)
    key: str = Field(nullable=False, index=True)
    value: Optional[Json] = Field(default=None, sa_type=JSON)
    app_id: str = Field(foreign_key="app.id", nullable=False, index=True, ondelete="CASCADE")
    parent_id: Optional[str] = Field(default=None, foreign_key="content.id")
    children: List["Content"] = Relationship(back_populates="parent", sa_relationship_kwargs={"remote_side": "Content.id"})
    parent: Optional["Content"] = Relationship(back_populates="children")
    app: App = Relationship(back_populates="content")

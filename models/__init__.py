from enum import Enum
import secrets
from typing import List, Optional
from uuid import uuid4
from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel, select
from datetime import datetime, timezone
from sqlmodel.ext.asyncio.session import AsyncSession

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
    is_active: bool = Field(default=True, nullable=False)
    users: List["User"] = Relationship(back_populates="domain")
    apps: List["App"] = Relationship(back_populates="domain")


class App(SQLModel, TimeStamp, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, nullable=False)
    name: Optional[str] = Field(default=None)
    secret: str = Field(nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    domain_id: str = Field(foreign_key="domain.id")
    domain: Domain = Relationship(back_populates="apps")


class User(SQLModel, TimeStamp, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, nullable=False)
    username: str = Field(nullable=False, unique=True, index=True, min_length=3)
    email: str = Field(nullable=False, unique=True, index=True)
    phone: str = Field(nullable=False, unique=True, index=True)
    password: str = Field(nullable=False)
    domain_id: Optional[str] = Field(default=None, foreign_key="domain.id", nullable=True)
    domain: Optional[Domain] = Relationship(back_populates="users")
    role_id: str = Field(foreign_key="role.id")
    role: Role = Relationship(back_populates="users")

    @classmethod
    async def is_first_user(self, session: AsyncSession) -> bool:
        result = await session.exec(select(User).join(Role).where(Role.name == RoleEnum.super_admin))
        return len(result.all()) == 0

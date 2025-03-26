from enum import Enum
import secrets
from typing import List, Optional
from uuid import uuid4
from pydantic import Json
from sqlalchemy import DateTime, Index, func
from sqlmodel import Field, Relationship, SQLModel, JSON
from datetime import datetime, timezone

#################### HELPERS ####################


def generate_uuid():
    return str(uuid4())


def generate_secret_key() -> str:
    length: int = 32
    return secrets.token_hex(length)


def default_time():
    return datetime.now(timezone.utc)

#################### ENUMS ####################


class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"
    super_admin = "super_admin"


class ContentTypeEnum(str, Enum):
    folder = "folder"
    file = "file"


class MediaTypeEnum(str, Enum):
    image = "image"
    video = "video"
    audio = "audio"
    other = "other"


class DocumentTypeEnum(str, Enum):
    pdf = "pdf"
    doc = "doc"
    xls = "xls"
    ppt = "ppt"
    txt = "txt"
    other = "other"

#################### MIXINS ####################


class BaseModel(SQLModel):
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, nullable=False)
    created_at: datetime = Field(default_factory=default_time, nullable=False, sa_type=DateTime(timezone=True))
    updated_at: datetime = Field(default_factory=default_time, nullable=False, sa_type=DateTime(timezone=True), sa_column_kwargs={"onupdate": func.now()})

#################### MANY TO MANY MODELS ####################


class UserApps(BaseModel, table=True):
    user_id: str = Field(foreign_key="user.id", primary_key=True, ondelete="CASCADE")
    app_id: str = Field(foreign_key="app.id", primary_key=True, ondelete="CASCADE")


class RolePermission(BaseModel, table=True):
    role_id: str = Field(foreign_key="role.id", primary_key=True)
    permission_id: str = Field(foreign_key="permission.id", primary_key=True)

#################### MODELS ####################


class Role(BaseModel, table=True):
    name: RoleEnum = Field(nullable=False, unique=True, index=True)
    users: List["User"] = Relationship(back_populates="role")
    permissions: List["Permission"] = Relationship(back_populates="roles", link_model=RolePermission)


class Permission(BaseModel, table=True):
    name: str = Field(nullable=False, unique=True)
    description: Optional[str] = Field(default=None)
    roles: List["Role"] = Relationship(back_populates="permissions", link_model=RolePermission)


class Domain(BaseModel, table=True):
    name: str = Field(nullable=False)
    host: str = Field(nullable=False, unique=True, index=True)
    url: Optional[str] = Field(default=None, nullable=True, unique=True, index=True)
    is_active: bool = Field(default=True, nullable=False)
    users: List["User"] = Relationship(back_populates="domain", cascade_delete=True)
    apps: List["App"] = Relationship(back_populates="domain", cascade_delete=True)


class App(BaseModel, table=True):
    name: str = Field(unique=True, index=True, nullable=False)
    slug: str = Field(unique=True, index=True, nullable=False)
    secret: str = Field(default_factory=generate_secret_key, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    domain_id: str = Field(foreign_key="domain.id", ondelete="CASCADE")
    domain: Domain = Relationship(back_populates="apps")
    users: List["User"] = Relationship(back_populates="apps", link_model=UserApps)
    media: List["Media"] = Relationship(back_populates="app", cascade_delete=True)
    content: List["Content"] = Relationship(back_populates="app", cascade_delete=True)
    documents: List["Document"] = Relationship(back_populates="app", cascade_delete=True)


class User(BaseModel, table=True):
    username: str = Field(nullable=False, unique=True, index=True, min_length=3)
    email: str = Field(nullable=False, unique=True, index=True)
    phone: str = Field(nullable=False, unique=True, index=True)
    password: str = Field(nullable=False)
    domain_id: Optional[str] = Field(default=None, foreign_key="domain.id", nullable=True, ondelete="CASCADE")
    role_id: str = Field(foreign_key="role.id")
    domain: Optional[Domain] = Relationship(back_populates="users")
    role: Role = Relationship(back_populates="users")
    apps: List["App"] = Relationship(back_populates="users", link_model=UserApps)
    uploaded_media: List["Media"] = Relationship(back_populates="uploaded_by")
    uploaded_documents: List["Document"] = Relationship(back_populates="uploaded_by")


class Content(BaseModel, table=True):
    name: str = Field(index=True, nullable=False)
    slug: str = Field(index=True, nullable=False)
    data: Optional[Json] = Field(default=None, sa_type=JSON)
    app_id: str = Field(foreign_key="app.id", nullable=False, index=True, ondelete="CASCADE")
    parent_id: Optional[str] = Field(default=None, foreign_key="content.id", index=True)
    children: Optional[List["Content"]] = Relationship(sa_relationship_kwargs={"lazy": "selectin", "join_depth": 100, "cascade": "delete"})
    app: App = Relationship(back_populates="content")
    __table_args__ = (
        Index("unique_slug_per_parent_and_app", "slug", "parent_id", "app_id", unique=True, postgresql_where="parent_id IS NOT NULL"),
        Index("unique_slug_app_when_no_parent", "slug", "app_id", unique=True, postgresql_where="parent_id IS NULL"),
    )


class Media(BaseModel, table=True):
    name: str = Field(index=True, nullable=False)
    original_filename: str = Field(nullable=False)
    file_key: str = Field(nullable=False, unique=True, index=True)
    file_extension: str = Field(nullable=False)
    file_size: int = Field(nullable=False)
    mime_type: str = Field(nullable=False)
    media_type: MediaTypeEnum = Field(nullable=False)
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    duration: Optional[float] = Field(default=None)
    alt_text: Optional[str] = Field(default=None)
    caption: Optional[str] = Field(default=None)
    meta: Optional[Json] = Field(default=None, sa_type=JSON)
    is_public: bool = Field(default=True, nullable=False)
    app_id: str = Field(foreign_key="app.id", nullable=False, index=True, ondelete="CASCADE")
    uploaded_by_id: str = Field(foreign_key="user.id", nullable=False)
    app: App = Relationship(back_populates="media")
    uploaded_by: "User" = Relationship(sa_relationship_kwargs={"lazy": "selectin", "primaryjoin": "Media.uploaded_by_id == User.id"})
    __table_args__ = (Index("index_media_app_id_created_at", "app_id", "created_at"), Index("index_media_media_type", "media_type"))


class Document(BaseModel, table=True):
    name: str = Field(index=True, nullable=False)
    original_filename: str = Field(nullable=False)
    file_key: str = Field(nullable=False, unique=True, index=True)
    file_extension: str = Field(nullable=False)
    file_size: int = Field(nullable=False)
    mime_type: str = Field(nullable=False)
    document_type: DocumentTypeEnum = Field(nullable=False)
    page_count: Optional[int] = Field(default=None)
    author: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    meta: Optional[Json] = Field(default=None, sa_type=JSON)
    is_public: bool = Field(default=False, nullable=False)
    app_id: str = Field(foreign_key="app.id", nullable=False, index=True, ondelete="CASCADE")
    uploaded_by_id: str = Field(foreign_key="user.id", nullable=False)
    app: App = Relationship(back_populates="documents")
    uploaded_by: "User" = Relationship(sa_relationship_kwargs={"lazy": "selectin", "primaryjoin": "Document.uploaded_by_id == User.id"})
    __table_args__ = (Index("index_document_app_id_created_at", "app_id", "created_at"), Index("index_document_document_type", "document_type"))

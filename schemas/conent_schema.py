from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import ConfigDict, Json
from sqlmodel import JSON, Field, SQLModel


class ContentCreateSchema(SQLModel):
    name: str
    data: Optional[Dict] = Field(default=None, sa_type=JSON)
    parent_id: Optional[UUID] = None


class ContentUpdateSchema(SQLModel):
    name: str
    data: Optional[Dict] = None


class ContentOutSchema(SQLModel):
    id: UUID
    app_id: UUID
    name: str
    slug: str
    data: Optional[Dict] = Field(default={}, sa_type=JSON)
    parent_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    children: List["ContentOutSchema"] = []

    model_config = ConfigDict(from_attributes=True)


ContentOutSchema.model_rebuild()

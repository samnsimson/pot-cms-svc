from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import ConfigDict
from sqlmodel import SQLModel


class ContentCreateSchema(SQLModel):
    name: str
    data: Optional[Dict] = None
    parent_id: Optional[UUID] = None


class ContentUpdateSchema(SQLModel):
    name: Optional[str] = None
    data: Optional[Dict] = None


class ContentOutSchema(SQLModel):
    id: UUID
    app_id: UUID
    name: str
    slug: str
    data: Optional[Dict] = None
    parent_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    children: List["ContentOutSchema"] = []

    model_config = ConfigDict(from_attributes=True)


ContentOutSchema.model_rebuild()

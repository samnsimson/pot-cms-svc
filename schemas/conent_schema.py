from datetime import datetime
from typing import Any, List, Optional, Union
from uuid import UUID
from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class ContentCreateSchema(SQLModel):
    key: str
    value: Optional[Any] = Field(default=None)
    parent_id: Optional[UUID] = Field(default=None)


class ContentOutSchema(SQLModel):
    id: UUID
    key: str
    value: Optional[Any] = Field(default=None)
    app_id: UUID
    parent_id: Optional[UUID] = Field(default=None)
    created_at: datetime
    updated_at: datetime
    children: List["ContentOutSchema"] = Field(default=[])

    model_config = ConfigDict(from_attributes=True)


ContentOutSchema.model_rebuild()

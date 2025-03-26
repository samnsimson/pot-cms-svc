from typing import Dict, Optional
from uuid import UUID
from sqlmodel import Field, SQLModel
from models import Media, MediaTypeEnum


class MediaMetaData(SQLModel):
    media_type: MediaTypeEnum
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_public: bool = True
    alt_text: Optional[str] = Field(None, min_length=1, max_length=512)
    caption: Optional[str] = Field(None, min_length=1, max_length=2048)
    meta: Optional[Dict] = None


class MediaUpdateSchema(SQLModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    alt_text: Optional[str] = Field(None, min_length=1, max_length=512)
    caption: Optional[str] = Field(None, min_length=1, max_length=2048)
    is_public: Optional[bool] = None
    meta: Optional[Dict] = None


class MediaResponse(SQLModel):
    id: UUID
    name: str
    media_type: str
    url: str | None
    alt_text: str | None
    caption: str | None
    is_public: bool

    @classmethod
    def from_model(cls, media: Media, url: str | None):
        return cls(
            id=media.id,
            name=media.name,
            media_type=media.media_type.value,
            url=url,
            alt_text=media.alt_text,
            caption=media.caption,
            is_public=media.is_public
        )

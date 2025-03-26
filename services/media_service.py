from uuid import UUID
from datetime import datetime
from typing import Optional, List
from io import BytesIO
from fastapi import UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, delete
from exceptions import InternalServerError, NotFoundException, BadRequestException
from schemas.media_schema import MediaCreateSchema, MediaUpdateSchema
from services.s3_service import S3Service
from models import App, User, Media, MediaTypeEnum
import os


class MediaService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.s3 = S3Service()

    async def get_media(self, app_id: UUID, media_id: UUID) -> Media:
        try:
            statement = select(Media).where(and_(Media.id == str(media_id), Media.app_id == str(app_id)))
            result = await self.session.exec(statement)
            media = result.one()
            return media
        except Exception as e:
            if isinstance(e, NotFoundException): raise
            raise NotFoundException(detail="Media not found") from e

    async def list_app_media(self, app_id: UUID, media_type: Optional[MediaTypeEnum] = None, limit: int = 100, offset: int = 0) -> List[Media]:
        try:
            statement = select(Media).where(Media.app_id == str(app_id))
            if media_type: statement = statement.where(Media.media_type == media_type)
            statement = statement.offset(offset).limit(limit).order_by(Media.created_at.desc())
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            raise InternalServerError(detail="Failed to fetch media list") from e

    async def upload_media(self, app_id: UUID, user_id: UUID, file: UploadFile, media_data: MediaCreateSchema) -> Media:
        try:
            app = await self.session.get(App, str(app_id))
            if not app: raise NotFoundException(detail="App not found")
            user = await self.session.get(User, str(user_id))
            if not user: raise NotFoundException(detail="User not found")

            original_filename = file.filename or "unnamed"
            file_extension = os.path.splitext(original_filename)[1].lower()
            if not file_extension: raise BadRequestException(detail="File must have an extension")
            if file.size is None or file.size <= 0: raise BadRequestException(detail="File cannot be empty")

            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            file_key = f"media/{app_id}/{timestamp}_{original_filename}"

            try:
                file_contents = await file.read()
                await self.s3.upload_file(file_key, BytesIO(file_contents), file.content_type)
            except Exception as e: raise InternalServerError(detail=f"Failed to upload file: {str(e)}") from e

            media = Media(
                name=media_data.name or original_filename,
                original_filename=original_filename,
                file_key=file_key,
                file_extension=file_extension,
                file_size=file.size,
                mime_type=file.content_type or "application/octet-stream",
                media_type=media_data.media_type,
                is_public=media_data.is_public,
                alt_text=media_data.alt_text,
                caption=media_data.caption,
                meta=media_data.meta,
                app_id=str(app_id),
                uploaded_by_id=str(user_id)
            )

            self.session.add(media)
            await self.session.commit()
            await self.session.refresh(media)
            return media
        except Exception as e:
            await self.session.rollback()
            if isinstance(e, (NotFoundException, BadRequestException, InternalServerError)): raise
            raise InternalServerError(detail="Failed to upload media") from e

    async def update_media(self, app_id: UUID, media_id: UUID, media_data: MediaUpdateSchema) -> Media:
        try:
            media = await self.get_media(app_id, media_id)
            if media_data.name is not None: media.name = media_data.name
            if media_data.alt_text is not None: media.alt_text = media_data.alt_text
            if media_data.caption is not None: media.caption = media_data.caption
            if media_data.is_public is not None: media.is_public = media_data.is_public
            if media_data.meta is not None: media.meta = media_data.meta

            self.session.add(media)
            await self.session.commit()
            await self.session.refresh(media)
            return media
        except Exception as e:
            await self.session.rollback()
            if isinstance(e, NotFoundException): raise
            raise InternalServerError(detail="Failed to update media") from e

    async def delete_media(self, app_id: UUID, media_id: UUID) -> bool:
        try:
            media = await self.get_media(app_id, media_id)
            try: await self.s3.delete_file(media.file_key)
            except Exception as e: raise InternalServerError(detail=f"Failed to delete file from storage: {str(e)}") from e
            statement = delete(Media).where(and_(Media.id == str(media_id), Media.app_id == str(app_id)))
            await self.session.exec(statement)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            if isinstance(e, (NotFoundException, InternalServerError)): raise
            raise InternalServerError(detail="Failed to delete media") from e

    async def get_media_url(self, media: Media) -> Optional[str]:
        try:
            if not media.is_public: return None
            return self.s3.generate_presigned_url(media.file_key)
        except Exception as e:
            raise InternalServerError(status_code=500, detail="Failed to generate media URL") from e

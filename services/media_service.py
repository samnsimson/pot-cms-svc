from uuid import UUID
from typing import Optional, List
from fastapi import UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, delete
from exceptions import InternalServerError, NotFoundException, BadRequestException
from schemas.media_schema import MediaMetaData, MediaUpdateSchema
from services.helpers.media_service_helper import MediaServiceHelper
from services.s3_service import S3Service
from models import Media, MediaTypeEnum


class MediaService(MediaServiceHelper):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.s3 = S3Service()
        super().__init__(session, self.s3)

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

    async def upload_media(self, app_id: UUID, user_id: UUID, file: UploadFile, meta_data: MediaMetaData) -> Media:
        try:
            await self._validate_app_and_user(app_id, user_id)
            original_filename, file_extension = self._process_filename(file)
            self._validate_file(file, file_extension)
            slug_name = self._generate_slug_name(meta_data.name, original_filename)
            file_key = self._generate_file_key(app_id, slug_name, file_extension)
            await self._upload_to_s3(file, file_key, app_id, user_id, meta_data, slug_name, original_filename)
            media = await self._create_media_record(app_id, user_id, file, meta_data, original_filename, file_extension, file_key, slug_name)
            return media
        except Exception as e:
            await self.session.rollback()
            if isinstance(e, (NotFoundException, BadRequestException, InternalServerError)): raise
            raise InternalServerError(detail="Failed to upload media") from e

    async def update_media(self, app_id: UUID, media_id: UUID, meta_data: MediaUpdateSchema) -> Media:
        try:
            media = await self.get_media(app_id, media_id)
            if meta_data.name is not None: media.name = meta_data.name
            if meta_data.alt_text is not None: media.alt_text = meta_data.alt_text
            if meta_data.caption is not None: media.caption = meta_data.caption
            if meta_data.is_public is not None: media.is_public = meta_data.is_public
            if meta_data.meta is not None: media.meta = meta_data.meta
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

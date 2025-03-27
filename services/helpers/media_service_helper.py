from uuid import UUID
from datetime import datetime
from typing import Optional
from fastapi import UploadFile
from slugify import slugify
from sqlmodel.ext.asyncio.session import AsyncSession
from exceptions import InternalServerError, NotFoundException, BadRequestException
from schemas.media_schema import MediaMetaData, MediaUpdateSchema
from services.s3_service import S3Service
from models import App, User, Media
import os


class MediaServiceHelper:
    def __init__(self, session: AsyncSession, s3: S3Service):
        self.session = session
        self.s3 = s3

    async def _validate_app_and_user(self, app_id: UUID, user_id: UUID) -> None:
        app = await self.session.get(App, str(app_id))
        if not app: raise NotFoundException(detail="App not found")
        user = await self.session.get(User, str(user_id))
        if not user: raise NotFoundException(detail="User not found")

    def _process_filename(self, file: UploadFile) -> tuple[str, str]:
        original_filename = file.filename or "unnamed"
        filename_without_ext, file_extension = os.path.splitext(original_filename)
        return original_filename, file_extension.lower()

    def _validate_file(self, file: UploadFile, file_extension: str) -> None:
        if not file_extension: raise BadRequestException(detail="File must have an extension")
        if file.size is None or file.size <= 0: raise BadRequestException(detail="File cannot be empty")

    def _generate_slug_name(self, custom_name: Optional[str], original_filename: str) -> str:
        filename_without_ext = os.path.splitext(original_filename)[0]
        name_to_slugify = custom_name or filename_without_ext
        slug_name = slugify(name_to_slugify)
        return slug_name if slug_name else "file"

    def _generate_file_key(self, app_id: UUID, slug_name: str, file_extension: str) -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        final_filename = f"{slug_name}{file_extension}"
        return f"media/{app_id}/{timestamp}_{final_filename}"

    async def _upload_to_s3(self, file: UploadFile, file_key: str, app_id: UUID, user_id: UUID, meta_data: MediaMetaData, slug_name: str, original_filename: str) -> None:
        try:
            file_contents = await file.read()
            meta = {'name': slug_name, 'app_id': str(app_id), 'original_filename': original_filename,
                    'media_type': meta_data.media_type.value, 'uploaded_by': str(user_id)}
            await self.s3.upload_file(file_key, file_contents, file.content_type, meta)
        except Exception as e: raise InternalServerError(detail=f"Failed to upload file: {str(e)}") from e

    async def _create_media_record(self, app_id: UUID, user_id: UUID, file: UploadFile, meta_data: MediaMetaData, original_filename: str, file_extension: str, file_key: str, file_path: str, slug_name: str) -> Media:
        media = Media(name=slug_name, original_filename=original_filename, file_key=file_key, file_path=file_path, file_extension=file_extension.lstrip('.'), file_size=file.size, mime_type=file.content_type or "application/octet-stream",
                      media_type=meta_data.media_type, is_public=meta_data.is_public, alt_text=meta_data.alt_text, caption=meta_data.caption, meta=meta_data.meta, app_id=str(app_id), uploaded_by_id=str(user_id))
        self.session.add(media)
        await self.session.commit()
        await self.session.refresh(media)
        return media

    def _update_media_values(self, meta_data: MediaUpdateSchema, media: Media):
        if meta_data.name is not None: media.name = meta_data.name
        if meta_data.alt_text is not None: media.alt_text = meta_data.alt_text
        if meta_data.caption is not None: media.caption = meta_data.caption
        if meta_data.is_public is not None: media.is_public = meta_data.is_public
        if meta_data.meta is not None: media.meta = meta_data.meta
        return media

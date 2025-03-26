from typing import List
from uuid import UUID
from fastapi import APIRouter
from starlette import status
from dependencies import session_dependency, user_dependency, file_dependency
from schemas.media_schema import MediaCreateSchema, MediaResponse, MediaUpdateSchema
from services.media_service import MediaService


router = APIRouter(prefix="/media", tags=["Media"])


@router.get("/{app_id}/{media_id}", operation_id="get_media", status_code=status.HTTP_200_OK, response_model=MediaResponse)
async def get_media(app_id: UUID, media_id: UUID, session: session_dependency):
    service = MediaService(session)
    media = await service.get_media(app_id, media_id)
    url = await service.get_media_url(media)
    return MediaResponse.from_model(media, url)


@router.get("/{app_id}", operation_id="list_app_media", status_code=status.HTTP_200_OK, response_model=List[MediaResponse])
async def list_app_media(session: session_dependency, app_id: UUID, media_type: str | None = None, limit: int = 100, offset: int = 0):
    service = MediaService(session)
    media_list = await service.list_app_media(app_id, media_type, limit, offset)
    return [MediaResponse.from_model(media, await service.get_media_url(media)) for media in media_list]


@router.post("/upload", operation_id="upload_media", status_code=status.HTTP_201_CREATED, response_model=MediaResponse)
async def upload_media(app_id: UUID, session: session_dependency, current_user: user_dependency, file: file_dependency, data: MediaCreateSchema):
    service = MediaService(session)
    media = await service.upload_media(app_id, current_user["id"], file, data)
    url = await service.get_media_url(media)
    return MediaResponse.from_model(media, url)


@router.put("/{app_id}/{media_id}", operation_id="update_media", status_code=status.HTTP_200_OK, response_model=MediaResponse)
async def update_media(app_id: UUID, media_id: UUID, update_data: MediaUpdateSchema, session: session_dependency, current_user: user_dependency):
    service = MediaService(session)
    media = await service.update_media(app_id, media_id, update_data)
    url = await service.get_media_url(media)
    return MediaResponse.from_model(media, url)


@router.delete("/{app_id}/{media_id}", operation_id="delete_media", status_code=status.HTTP_200_OK)
async def delete_media(app_id: UUID, media_id: UUID, session: session_dependency, current_user: user_dependency):
    service = MediaService(session)
    await service.delete_media(app_id, media_id)
    return {"status": "success", "message": "Media deleted"}

from uuid import UUID
from fastapi import APIRouter
from starlette import status
from dependencies import session_dependency
from services.media_service import MediaService


router = APIRouter(prefix="/media", tags=["Media"])


@router.get("/{app_id}/{media_id}", operation_id="get_media", status_code=status.HTTP_200_OK)
async def get_media(app_id: UUID, media_id: UUID, session: session_dependency):
    service = MediaService(session)
    pass


@router.get("/{app_id}", operation_id="list_app_media", status_code=status.HTTP_200_OK)
async def list_app_media(app_id: UUID, session: session_dependency):
    pass


@router.post("/upload", operation_id="upload_media", status_code=status.HTTP_201_CREATED)
async def upload_media(app_id: UUID, session: session_dependency):
    pass


@router.put("/{app_id}/{media_id}", operation_id="update_media", status_code=status.HTTP_201_CREATED)
async def update_media(app_id: UUID, media_id: UUID, session: session_dependency):
    pass


@router.delete("/{app_id}/{media_id}", operation_id="delete_media", status_code=status.HTTP_200_OK)
async def delete_media(app_id: UUID, media_id: UUID, session: session_dependency):
    pass

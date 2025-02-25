from typing import Sequence
from uuid import UUID
from fastapi import APIRouter
from starlette import status
from dependencies import session_dependency
from schemas.conent_schema import ContentCreateSchema, ContentOutSchema
from services.conent_service import ContentService

content_service = ContentService()

router = APIRouter(prefix="/content", tags=["Content"])


@router.post("/{app_id}", operation_id="create_content", status_code=status.HTTP_201_CREATED, response_model=ContentOutSchema)
async def create_content(app_id: UUID, content_data: ContentCreateSchema, session: session_dependency):
    content = await content_service.create_content(app_id, content_data, session)
    return content


@router.get("/{app_id}", operation_id="get_content", status_code=status.HTTP_200_OK, response_model=Sequence[ContentOutSchema])
async def get_content(app_id: UUID, session: session_dependency):
    return await content_service.get_content(app_id, session)

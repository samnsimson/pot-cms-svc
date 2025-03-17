import json
from typing import Sequence
from uuid import UUID
from fastapi import APIRouter, Response
from starlette import status
from dependencies import session_dependency, user_dependency
from schemas.conent_schema import ContentCreateSchema, ContentOutSchema, ContentUpdateSchema
from services.conent_service import ContentService

content_service = ContentService()

router = APIRouter(prefix="/content", tags=["Content"])


@router.get("/export", operation_id="export_content", status_code=status.HTTP_200_OK)
async def export_content(app_id: UUID, content_id: UUID, session: session_dependency):
    data = await content_service.export_content(app_id, content_id, session)
    json_data = json.dumps(data, indent=4)
    response = Response(content=json_data, media_type="application/json")
    response.headers["Content-Disposition"] = f"attachment; filename=content-{content_id}.json"
    return response


@router.post("/{app_id}", operation_id="create_content", status_code=status.HTTP_201_CREATED, response_model=ContentOutSchema)
async def create_content(app_id: UUID, content_data: ContentCreateSchema, session: session_dependency):
    content = await content_service.create_content(app_id, content_data, session)
    return content


@router.get("/{app_id}", operation_id="get_content", status_code=status.HTTP_200_OK, response_model=Sequence[ContentOutSchema])
async def get_content(app_id: UUID, session: session_dependency):
    return await content_service.get_content(app_id, session)


@router.put("/{app_id}", operation_id="update_content", status_code=status.HTTP_200_OK, response_model=ContentOutSchema)
async def update_content(app_id: UUID, content_id: UUID, data: ContentUpdateSchema, session: session_dependency, user: user_dependency):
    return await content_service.update_content(app_id=app_id, content_id=content_id, data=data, session=session)

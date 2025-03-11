from typing import List
from uuid import UUID
from fastapi import APIRouter, Request
from starlette import status
from dependencies import session_dependency, user_dependency
from exceptions import ForbiddenException, NotFoundException
from models import RoleEnum
from schemas.apps_schema import AppCreateSchema, AppDeleteOutSchema, AppOutSchema
from schemas.user_schema import UserOutSchema
from services.apps_service import AppsService

app_service = AppsService()

router = APIRouter(prefix="/apps", tags=['Apps'])


@router.get("", operation_id="list_apps", status_code=status.HTTP_200_OK, response_model=List[AppOutSchema])
async def list_apps(user_data: user_dependency, session: session_dependency):
    apps = await app_service.get_apps(user_data, session)
    return apps


@router.get("/{key}", operation_id="get_app_by_id_or_slug", status_code=status.HTTP_200_OK, response_model=AppOutSchema)
async def get_app(key: UUID | str, user_data: user_dependency, session: session_dependency):
    app = await app_service.get_app_by_id_or_slug(key=key, user_data=user_data, session=session)
    if not app: raise NotFoundException("App not found")
    return app


@router.get("/{id}/users", operation_id="get_app_users", status_code=status.HTTP_200_OK, response_model=List[UserOutSchema])
async def get_app_users(id: UUID, session: session_dependency):
    users = await app_service.get_app_users(app_id=id, session=session)
    return users


@router.post("", operation_id="create_app", status_code=status.HTTP_201_CREATED, response_model=AppOutSchema)
async def create_app(app_data: AppCreateSchema, user_data: user_dependency, session: session_dependency):
    if user_data.role != RoleEnum.super_admin: raise ForbiddenException("Not authorized")
    new_app = await app_service.create_app(app_data, user_data, session)
    return new_app


@router.delete("/{id}", operation_id="delete_app", status_code=status.HTTP_200_OK, response_model=AppDeleteOutSchema)
async def delete_app(id: UUID, user_data: user_dependency, session: session_dependency):
    if user_data.role != RoleEnum.super_admin: raise ForbiddenException("Not authorized")
    await app_service.delete_app(id=id, session=session)
    return AppDeleteOutSchema(id=id, status="deleted")

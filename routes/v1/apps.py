from typing import List
from fastapi import APIRouter, Request
from starlette import status
from dependencies import session_dependency
from exceptions import ForbiddenException
from models import RoleEnum
from schemas.apps_schema import AppCreateSchema, AppOutSchema
from services.apps_service import AppsService
from utils import get_current_user

app_service = AppsService()

router = APIRouter(prefix="/apps", tags=['Apps'])


@router.get("", operation_id="get_apps", status_code=status.HTTP_200_OK, response_model=List[AppOutSchema])
async def get(request: Request, session: session_dependency):
    user_data = get_current_user(request)
    apps = await app_service.get_apps(user_data, session)
    return apps


@router.post("", operation_id="create_app", status_code=status.HTTP_201_CREATED, response_model=AppOutSchema)
async def create_app(request: Request, app_data: AppCreateSchema, session: session_dependency):
    user_data = get_current_user(request)
    if user_data.role != RoleEnum.super_admin: raise ForbiddenException("Not authorized")
    new_app = await app_service.create_app(app_data, user_data, session)
    return new_app

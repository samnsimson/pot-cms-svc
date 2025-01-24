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


@router.get("", status_code=status.HTTP_200_OK)
async def get(request: Request):
    return {"response": request.state}


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AppOutSchema)
async def create_app(request: Request, app_data: AppCreateSchema, session: session_dependency):
    user_data = get_current_user(request)
    if user_data.role != RoleEnum.super_admin: raise ForbiddenException("Not authorized")
    return await app_service.create_app(app_data, user_data, session)

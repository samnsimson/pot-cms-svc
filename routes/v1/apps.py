from fastapi import APIRouter, Request
from starlette import status

from exceptions import ForbiddenException
from models import RoleEnum

router = APIRouter(prefix="/client", tags=['Client'])


@router.get("", status_code=status.HTTP_200_OK)
async def get(request: Request):
    return {"response": request.state}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_app(request: Request):
    if request.state.__getattr__("role") != RoleEnum.super_admin: raise ForbiddenException("Not authorized")
    return "Success"

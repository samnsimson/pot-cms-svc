from fastapi import APIRouter, Request
from starlette import status
from dependencies import session_dependency
from exceptions import ForbiddenException, InternalServerError
from models import RoleEnum
from schemas.domain_schema import DomainCreateSchema, DomainOutSchema
from services.domain_service import DomainService
from utils import get_current_user

domain_service = DomainService()

router = APIRouter(prefix="/domain", tags=["Domain"])


@router.post("", operation_id="create_domain", status_code=status.HTTP_201_CREATED, response_model=DomainOutSchema)
async def create_domain(domain_data: DomainCreateSchema, request: Request, session: session_dependency):
    current_user = get_current_user(request)
    if current_user.role is not RoleEnum.super_admin: raise ForbiddenException("User not authorized to create domain")
    new_domain = await domain_service.create_domain(domain_data, current_user, session)
    return DomainOutSchema.model_validate(new_domain)

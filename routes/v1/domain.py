from fastapi import APIRouter
from starlette import status
from dependencies import session_dependency, user_dependency
from exceptions import ForbiddenException
from models import RoleEnum
from schemas.domain_schema import DomainCreateSchema, DomainOutSchema
from services.domain_service import DomainService

domain_service = DomainService()

router = APIRouter(prefix="/domain", tags=["Domain"])


@router.post("", operation_id="create_domain", status_code=status.HTTP_201_CREATED, response_model=DomainOutSchema)
async def create_domain(domain_data: DomainCreateSchema, current_user: user_dependency, session: session_dependency):
    if current_user.role is not RoleEnum.super_admin: raise ForbiddenException("User not authorized to create domain")
    new_domain = await domain_service.create_domain(domain_data, current_user, session)
    return DomainOutSchema.model_validate(new_domain)

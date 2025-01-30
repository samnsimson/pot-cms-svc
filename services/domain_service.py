from exceptions import ConflictException, ForbiddenException, InternalServerError
from models import Domain, User
from schemas.domain_schema import DomainCreateSchema
from schemas.utils_schema import CurrentUser
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError


class DomainService:
    async def create_domain(self, domain_data: DomainCreateSchema, current_user: CurrentUser, session: AsyncSession):
        try:
            user = await session.get(User, current_user.id)
            if user.domain_id is not None: raise ForbiddenException("User cannot create multiple domain")
            if not user: raise ForbiddenException("User not authorized to create domain")
            domain = Domain(**domain_data.model_dump(), users=[user])
            session.add(domain)
            await session.commit()
            await session.refresh(domain)
            return domain
        except IntegrityError as e:
            await session.rollback()
            if "duplicate key" in str(e.orig).lower(): raise ConflictException("Domain with this host already exists")
            else: raise InternalServerError("An unexpected database error occurred")

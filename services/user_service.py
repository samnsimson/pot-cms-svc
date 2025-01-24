from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from exceptions import BadRequestException, InternalServerError, UnauthorizedException
from models import Domain, Role, RoleEnum, User
from schemas.user_schema import UserCreateSchema
from passlib.context import CryptContext
from services.roles_and_permission import RolesAndPermission


class UserService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.roles_service = RolesAndPermission()

    def __verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def __hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def register_user(self, user_data: UserCreateSchema, session: AsyncSession):
        try:
            hashed_password = self.__hash_password(user_data.password)
            new_user = User(**user_data.model_dump(exclude={"password", "domain"}), password=hashed_password)

            # ASSIGN SUPER ADMIN ROLE TO FIRST USER
            role = await self.roles_service.get_role_by_name(RoleEnum.super_admin, session)
            if role is not None: new_user.role_id = role.id

            # CREATE DOMAIN IF PROVIDED
            if user_data.domain is not None: new_user.domain = Domain(name=user_data.domain.name, host=user_data.domain.host)

            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user
        except IntegrityError as e:
            await session.rollback()
            if "email" in str(e.orig): raise BadRequestException("Email already in use")
            elif "phone" in str(e.orig): raise BadRequestException("Phone already in use")
            elif "username" in str(e.orig): raise BadRequestException("Username already in use")
            else: raise InternalServerError(f"Error: {str(e)}")

    async def authenticate_user(self, email: str, password: str, session: AsyncSession):
        try:
            result = await session.exec(select(User, Role).join(Role, Role.id == User.role_id).where(User.email == email))
            existing_user, role = result.first()
            if existing_user is None: raise UnauthorizedException("User not found")
            if not self.__verify_password(password, existing_user.password): raise UnauthorizedException("Wrong Password")
            return existing_user, role
        except NoResultFound: raise UnauthorizedException("User not found")
        except Exception as e: raise InternalServerError(f"Unexpected error: {str(e)}")

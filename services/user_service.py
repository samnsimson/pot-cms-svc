from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from exceptions import BadRequestException, InternalServerError, NotFoundException, UnauthorizedException
from models import User
from schemas.user_schema import UserCreateSchema
from passlib.context import CryptContext


class UserService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def __hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def register_user(self, user_data: UserCreateSchema, session: AsyncSession):
        try:
            hashed_password = self.__hash_password(user_data.password)
            new_user = User(**user_data.model_dump(exclude={"password"}), password=hashed_password)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user
        except IntegrityError as e:
            await session.rollback()
            if "email" in str(e.orig): raise BadRequestException("Email already in use")
            elif "phone" in str(e.orig): raise BadRequestException("Phone already in use")
            elif "username" in str(e.orig): raise BadRequestException("Username already in use")
            else: raise InternalServerError("Unexpected error occurred while registering user.")

    async def authenticate_user(self, email: str, password: str, session: AsyncSession):
        result = await session.exec(select(User).where(User.email == email))
        existing_user = result.first()
        if existing_user is None: raise NotFoundException("User not found")
        if not self.__verify_password(password, existing_user.password): raise UnauthorizedException("Wrong Password")
        return existing_user

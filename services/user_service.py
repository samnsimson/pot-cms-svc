from sqlmodel.ext.asyncio.session import AsyncSession
from models import User
from schemas.user_schema import UserCreateSchema
from passlib.context import CryptContext


class UserService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def register_user(self, user_data: UserCreateSchema, session: AsyncSession):
        hashed_password = self.__hash_password(user_data.password)
        new_user = User(**user_data.model_dump(exclude={"password"}), password=hashed_password)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

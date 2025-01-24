from sqlmodel import select
from models import Role, RoleEnum
from sqlmodel.ext.asyncio.session import AsyncSession


class RolesAndPermission:
    async def get_role_by_name(self, role_name: RoleEnum, session: AsyncSession):
        result = await session.exec(select(Role).where(Role.name == role_name))
        role = result.one_or_none()
        return role

    async def get_role_by_id(self, role_id: str, session: AsyncSession):
        result = await session.exec(select(Role).where(Role.id == role_id))
        role = result.first()
        return role

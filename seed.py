from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models import Role, RoleEnum


async def seed_roles(session: AsyncSession):
    result = await session.exec(select(Role))
    existing_roles = result.all()
    if not existing_roles:
        roles = [Role(name=RoleEnum.super_admin), Role(name=RoleEnum.admin), Role(name=RoleEnum.user)]
        session.add_all(roles)
        await session.commit()
        print("Roles populated successfully.")

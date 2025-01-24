from sqlmodel import select
from models import Role, RoleEnum
from database import async_session


async def seed_roles():
    async with async_session() as session:
        result = await session.exec(select(Role))
        existing_roles = result.all()
        if not existing_roles:
            roles = [Role(name=RoleEnum.super_admin), Role(name=RoleEnum.admin), Role(name=RoleEnum.user)]
            session.add_all(roles)
            await session.commit()
            print("Roles populated successfully.")

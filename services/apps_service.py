from sqlmodel import select
from exceptions import ForbiddenException, UnprocessableEntityException
from models import App, User, UserApps
from schemas.apps_schema import AppCreateSchema
from sqlmodel.ext.asyncio.session import AsyncSession
from schemas.utils_schema import CurrentUser


class AppsService:
    async def get_apps(self, user_data: CurrentUser, session: AsyncSession):
        if not user_data.id: raise UnprocessableEntityException("User data not available")
        query = select(App).join(App.users).where(User.id == user_data.id)
        result = await session.exec(query)
        apps = result.all()
        return apps

    async def create_app(self, app_data: AppCreateSchema, user_data: CurrentUser, session: AsyncSession):
        if not user_data.host: raise UnprocessableEntityException("Unable to create an app without a host")
        user = await session.get(User, user_data.id)
        if not user: raise ForbiddenException("User not found")
        new_app = App(name=app_data.name, domain_id=user_data.host, users=[user])
        session.add(new_app)
        await session.commit()
        await session.refresh(new_app)
        return new_app

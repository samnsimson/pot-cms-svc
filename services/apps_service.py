from uuid import UUID
from sqlmodel import and_, select
from sqlalchemy.orm import joinedload
from exceptions import ForbiddenException, NotFoundException, UnprocessableEntityException
from models import App, User
from schemas.apps_schema import AppCreateSchema
from sqlmodel.ext.asyncio.session import AsyncSession
from schemas.utils_schema import CurrentUser


class AppsService:
    async def get_app_by_id(self, id: UUID, user_data: CurrentUser, session: AsyncSession):
        if not user_data.id: raise UnprocessableEntityException("User data not available")
        query = select(App).join(App.users).where(and_(User.id == user_data.id, App.id == str(id))).options(joinedload(App.users))
        result = await session.exec(query)
        app = result.first()
        return app

    async def get_apps(self, user_data: CurrentUser, session: AsyncSession):
        if not user_data.id: raise UnprocessableEntityException("User data not available")
        query = select(App).join(App.users).where(User.id == user_data.id).options(joinedload(App.users))
        result = await session.exec(query)
        apps = result.unique().all()
        return apps

    async def get_app_users(self, app_id: UUID, session: AsyncSession):
        query = select(User).join(User.apps).where(App.id == str(app_id))
        result = await session.exec(query)
        return result.unique().all()

    async def create_app(self, app_data: AppCreateSchema, user_data: CurrentUser, session: AsyncSession):
        if not user_data.host: raise UnprocessableEntityException("Unable to create an app without a host")
        user = await session.get(User, user_data.id)
        if not user: raise ForbiddenException("User not found")
        new_app = App(name=app_data.name, domain_id=user_data.host, users=[user])
        session.add(new_app)
        await session.commit()
        await session.refresh(new_app)
        return new_app

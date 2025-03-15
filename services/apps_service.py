from uuid import UUID
from slugify import slugify
from sqlmodel import and_, select
from sqlalchemy.orm import joinedload
from exceptions import ForbiddenException, NotFoundException, UnprocessableEntityException
from models import App, User
from schemas.apps_schema import AppCreateSchema
from sqlmodel.ext.asyncio.session import AsyncSession
from schemas.utils_schema import CurrentUser
from sqlalchemy.exc import IntegrityError


class AppsService:
    def __isUUID(slef, string: str):
        is_uuid = True
        try: UUID(str(string))
        except ValueError: is_uuid = False
        return is_uuid

    async def get_app_by_id_or_slug(self, key: UUID | str, user_data: CurrentUser, session: AsyncSession):
        if not user_data.id: raise UnprocessableEntityException("User data not available")
        is_uuid = self.__isUUID(key)
        id_or_slug = App.id == str(key) if is_uuid else App.slug == key
        query = select(App).join(App.users).where(and_(User.id == user_data.id, id_or_slug)).options(joinedload(App.users))
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
        try:
            if not user_data.domain: raise UnprocessableEntityException("Unable to create an app without a host")
            user = await session.get(User, user_data.id)
            if not user: raise ForbiddenException("User not found")
            slug = slugify(app_data.name, separator="-")
            new_app = App(name=app_data.name, domain_id=user_data.domain, slug=slug, users=[user])
            session.add(new_app)
            await session.commit()
            await session.refresh(new_app)
            return new_app
        except IntegrityError as e:
            print(str(e))
            await session.rollback()
            if "name" in str(e): raise UnprocessableEntityException("Cannot create duplicate app")
            if "slug" in str(e): raise UnprocessableEntityException("Cannot create duplicate slug")

    async def delete_app(self, id: UUID, session: AsyncSession):
        app = await session.get(App, str(id))
        if not app: raise NotFoundException("App not found")
        await session.delete(app)
        await session.commit()
        return True

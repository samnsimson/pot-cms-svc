from uuid import UUID
from slugify import slugify
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, asc
from exceptions import BadRequestException, InternalServerError, NotFoundException, UnprocessableEntityException
from models import Content
from schemas.conent_schema import ContentCreateSchema, ContentUpdateSchema
from sqlmodel.ext.asyncio.session import AsyncSession


class ContentService:
    async def create_content(self, app_id: UUID, content_data: ContentCreateSchema, session: AsyncSession):
        try:
            slug = slugify(content_data.name, separator="-")
            parent_id = str(content_data.parent_id) if content_data.parent_id else None
            content = Content(app_id=str(app_id), slug=slug, parent_id=parent_id, name=content_data.name, data=content_data.data)
            session.add(content)
            await session.commit()
            await session.refresh(content)
            return content
        except IntegrityError as e:
            await session.rollback()
            if "slug" in str(e): raise UnprocessableEntityException(detail="Duplicate content name")
        except Exception as e:
            await session.rollback()
            raise InternalServerError(detail=str(e))

    async def get_content(self, app_id: UUID, session: AsyncSession):
        statement = select(Content).where(Content.app_id == str(app_id), Content.parent_id == None).order_by(asc(Content.created_at))
        result = await session.exec(statement)
        return result.all()

    async def update_content(self, app_id: UUID, content_id: UUID, data: ContentUpdateSchema, session: AsyncSession):
        try:
            print(data)
            statement = select(Content).where(Content.app_id == str(app_id), Content.id == str(content_id))
            result = await session.exec(statement)
            content = result.one_or_none()
            if not content: raise NotFoundException(detail="Content not found")
            if data.name:
                content.name = data.name
                content.slug = slugify(data.name, separator="-")
            content.data = data.data if data.data else {}
            session.add(content)
            await session.commit()
            await session.refresh(content)
            return content
        except IntegrityError as ie:
            await session.rollback()
            raise BadRequestException(detail=str(ie))

    async def export_content(self, app_id: UUID, content_id: UUID, session: AsyncSession):
        try:
            statement = select(Content).where(Content.app_id == str(app_id), Content.id == str(content_id))
            result = await session.exec(statement)
            content = result.one_or_none()
            if not content: raise NotFoundException(detail="Content not found")
            if content.data is None: raise NotFoundException(detail="Cannot export empty data")
            return content.data
        except IntegrityError as ie:
            await session.rollback()
            raise BadRequestException(detail=str(ie))

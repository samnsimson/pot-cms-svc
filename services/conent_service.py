from uuid import UUID
from slugify import slugify
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from exceptions import InternalServerError, UnprocessableEntityException
from models import Content
from schemas.conent_schema import ContentCreateSchema
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
        statement = select(Content).where(Content.app_id == str(app_id), Content.parent_id == None)
        result = await session.exec(statement)
        return result.all()

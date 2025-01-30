from uuid import UUID
from sqlalchemy.orm import joinedload
from sqlmodel import select
from models import Content
from schemas.conent_schema import ContentCreateSchema
from sqlmodel.ext.asyncio.session import AsyncSession


class ContentService:
    async def create_content(app_id: UUID, content_data: ContentCreateSchema, session: AsyncSession):
        content = Content(app_id=app_id, **content_data.model_dump())
        session.add(content)
        await session.commit()
        await session.refresh(content)
        return content

    async def get_content(app_id: UUID, session: AsyncSession):
        statement = select(Content).where(Content.app_id == app_id).options(joinedload(Content.children))
        result = await session.exec(statement)
        return result.all()

from sqlmodel.ext.asyncio.session import AsyncSession


class MediaService:
    def __init__(self, session: AsyncSession):
        self.session = session

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from config import config


url = f"postgresql+asyncpg://{config.DATABASE_USER}:{config.DATABASE_PASS}@{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}"
async_engine = create_async_engine(url=url, echo=True, future=True, pool_size=10, max_overflow=20)


async def get_async_session():
    async_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


def init_db():
    SQLModel.metadata.create_all(async_engine)

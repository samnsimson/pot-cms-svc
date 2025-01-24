from typing import Annotated
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from database import get_async_session


session_dependency = Annotated[AsyncSession, Depends(get_async_session)]

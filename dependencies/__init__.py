from typing import Annotated
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from database import get_async_session
from schemas.utils_schema import CurrentUser
from utils import get_current_user


session_dependency = Annotated[AsyncSession, Depends(get_async_session)]
user_dependency = Annotated[CurrentUser, Depends(get_current_user)]

from typing import Annotated
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from database import get_async_session
from services.auth_service import AuthService

auth_service = AuthService()

session_dependency = Annotated[AsyncSession, Depends(get_async_session)]
auth_dependency = Depends(auth_service.get_current_user)

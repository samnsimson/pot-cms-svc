from typing import Annotated
from fastapi import Depends, File, UploadFile
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from cache import CacheClient, get_redis
from database import get_async_session
from schemas.utils_schema import CurrentUser
from utils import get_current_user, get_http_client


session_dependency = Annotated[AsyncSession, Depends(get_async_session)]
user_dependency = Annotated[CurrentUser, Depends(get_current_user)]
cache_dependency = Annotated[CacheClient, Depends(get_redis)]
http_dependency = Annotated[AsyncClient, Depends(get_http_client)]
file_dependency = Annotated[UploadFile, File(description="Media file to upload")]

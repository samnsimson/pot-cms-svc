from fastapi import APIRouter
from starlette import status
from schemas.user_schema import UserCreateSchema, UserOutSchema
from services.user_service import UserService
from dependency import session_dependency

user_service = UserService()
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
async def login():
    return {"message": "login success"}


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOutSchema)
async def register(user_data: UserCreateSchema, session: session_dependency):
    return await user_service.register_user(user_data=user_data, session=session)

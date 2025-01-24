from datetime import timedelta
from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from schemas.auth_schema import LoginResponseSchema
from schemas.user_schema import UserCreateSchema, UserOutSchema
from services.auth_service import AuthService
from services.user_service import UserService
from dependencies import session_dependency

user_service = UserService()
auth_service = AuthService()

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponseSchema)
async def login(session: session_dependency, response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user, role = await user_service.authenticate_user(form_data.username, form_data.password, session)
    access_token = auth_service.create_access_token({"sub": user.id, "host": user.domain_id, "role": role.name})
    refresh_token = auth_service.create_refresh_token({"sub": user.id, "host": user.domain_id, "role": role.name})
    response.set_cookie("refresh_token", refresh_token, timedelta(days=7), httponly=True)
    return {"access_token": access_token, "token_type": "Bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOutSchema)
async def register(user_data: UserCreateSchema, session: session_dependency):
    return await user_service.register_user(user_data=user_data, session=session)

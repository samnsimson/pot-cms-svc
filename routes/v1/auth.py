from datetime import timedelta
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from schemas.auth_schema import AuthResponseSchema, RefreshBody
from schemas.user_schema import UserCreateSchema, UserOutSchema
from services.auth_service import AuthService
from services.user_service import UserService
from dependencies import session_dependency

user_service = UserService()
auth_service = AuthService()

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", operation_id="login", status_code=status.HTTP_200_OK, response_model=AuthResponseSchema)
async def login(session: session_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    user, role, domain = await user_service.authenticate_user(form_data.username, form_data.password, session)
    token_payload = {"sub": user.id, "domain": domain.id, "host": domain.name, "role": role.name}
    access_token_timedelta = timedelta(minutes=30)
    refresh_token_timedelta = timedelta(days=7)
    access_token = auth_service.create_access_token(token_payload, access_token_timedelta)
    refresh_token = auth_service.create_refresh_token(token_payload, refresh_token_timedelta)
    return AuthResponseSchema(status="Success", user_id=user.id, host=domain.name, role=role.name, redirect_url="/", access_token=access_token, refresh_token=refresh_token, token_type="Bearer", token_max_age=access_token_timedelta.total_seconds())


@router.post("/register", operation_id="signup", status_code=status.HTTP_201_CREATED, response_model=UserOutSchema)
async def register(user_data: UserCreateSchema, session: session_dependency):
    return await user_service.register_user(user_data=user_data, session=session)


@router.post("/token/refresh", operation_id="refresh_token", status_code=status.HTTP_200_OK, response_model=AuthResponseSchema)
async def refresh_token(body: RefreshBody):
    payload = auth_service.verify_token(body.token)
    host = payload.get("host", None)
    role = payload.get("role", None)
    user_id = payload.get("sub", None)
    domain = payload.get("domain", None)
    access_token_timedelta = timedelta(minutes=30)
    access_token = auth_service.create_access_token({"sub": user_id, "host": host, "domain": domain, "role": role}, access_token_timedelta)
    return AuthResponseSchema(status="Success", user_id=user_id, host=host, role=role, redirect_url=None, access_token=access_token, refresh_token=body.token, token_type="Bearer", token_max_age=access_token_timedelta.total_seconds())

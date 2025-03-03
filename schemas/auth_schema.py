from sqlmodel import SQLModel


class LoginResponseSchema(SQLModel):
    status: str
    user_id: str
    email: str
    host: str
    redirect_url: str
    access_token: str
    token_type: str
    token_max_age: int


class ResfreshResponseSchema(SQLModel):
    access_token: str
    token_type: str

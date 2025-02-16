from sqlmodel import SQLModel


class LoginResponseSchema(SQLModel):
    status: str
    redirect_url: str
    access_token: str
    token_type: str


class ResfreshResponseSchema(SQLModel):
    access_token: str
    token_type: str

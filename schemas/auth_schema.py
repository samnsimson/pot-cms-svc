from sqlmodel import SQLModel


class LoginResponseSchema(SQLModel):
    access_token: str
    token_type: str


class ResfreshResponseSchema(SQLModel):
    access_token: str
    token_type: str

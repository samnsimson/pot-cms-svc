from sqlmodel import Field, SQLModel


class DomainSchema(SQLModel):
    name: str = Field(min_length=1)
    host: str = Field(regex=r'^[a-zA-Z0-9-]+$')


class DomainCreateSchema(DomainSchema):
    pass

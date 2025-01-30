from datetime import datetime
from sqlmodel import Field, SQLModel
from schemas.base_schema import ID


class DomainSchema(SQLModel):
    name: str = Field(min_length=1)
    host: str = Field(regex=r'^[a-zA-Z0-9-]+$')


class DomainCreateSchema(DomainSchema):
    pass


class DomainOutSchema(DomainSchema, ID):
    created_at: datetime
    updated_at: datetime

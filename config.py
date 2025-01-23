from pydantic_settings import BaseSettings
from pydantic import Field, ValidationError

class Settings(BaseSettings):
    PROJECT_NAME:str = Field(..., description="Project title")
    PROJECT_VERSION:str = Field(..., description="Project version")
    PROJECT_DESCRIPTION:str = Field(..., description="Project description")
    DATABASE_USER: str = Field(..., description="Database username")
    DATABASE_NAME: str = Field(..., description="Database name")
    DATABASE_HOST: str = Field(..., description="Database host")
    DATABASE_PASS: str = Field(..., description="Database password")
    DATABASE_PORT: str = Field(default="5432", description="Database port")

    class Config:
        env_file = ".env"


try:
    config = Settings()
except ValidationError as e:
    print("Environment configuration is invalid!")
    print(e)
    raise
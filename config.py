from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings
from pydantic import Field, ValidationError


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(description="Project title")
    PROJECT_VERSION: str = Field(description="Project version")
    PROJECT_DESCRIPTION: str = Field(description="Project description")
    DATABASE_USER: str = Field(description="Database username")
    DATABASE_NAME: str = Field(description="Database name")
    DATABASE_HOST: str = Field(description="Database host")
    DATABASE_PASS: str = Field(description="Database password")
    DATABASE_PORT: str = Field(default="5432", description="Database port")
    JWT_SECRET: str = Field(default=None, description="Secret key to encode JWT")
    JWT_ALGORITHM: str = Field(default=None, description="Algorithm used to encode JWT")
    AWS_ACCESS_KEY: str = Field(description="AWS Access Key")
    AWS_SECRET_KEY: str = Field(description="AWS Secret Key")
    AWS_REGION: str = Field(description="AWS Region")
    S3_BUCKET_NAME: str = Field(description="AWS Region")
    AWS_DIST_URL: str = Field(description="AWS Region")
    AUTH_SCHEME: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

    class Config:
        env_file = ".env"


try:
    config = Settings()
except ValidationError as e:
    print("Environment configuration is invalid!")
    print(e)
    raise

from datetime import datetime, timedelta, timezone
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config import config
from exceptions import UnauthorizedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class AuthService:
    def create_access_token(self, data: dict, expires_delta: timedelta = timedelta(minutes=30)):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict, expires_delta: timedelta = timedelta(days=7)):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str):
        try: return jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        except JWTError: raise UnauthorizedException(detail="Invalid token")

    def get_current_user(self, request: Request, token: str = Depends(oauth2_scheme)) -> str:
        try:
            payload = self.verify_token(token)
            user = payload.get("sub")
            if user is None: raise UnauthorizedException(detail="Could not validate credentials")
            setattr(request.state, "user", user)
            return user
        except Exception as e: raise UnauthorizedException(detail="Unauthorized")

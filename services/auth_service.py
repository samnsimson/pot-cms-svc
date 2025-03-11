from datetime import datetime, timedelta, timezone
from jose import ExpiredSignatureError, JWTError, jwt
from config import config
from exceptions import UnauthorizedException


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
        except ExpiredSignatureError: raise UnauthorizedException("Token has expired")
        except JWTError: raise UnauthorizedException("Invalid token")

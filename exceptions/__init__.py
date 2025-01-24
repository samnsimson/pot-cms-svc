from fastapi import HTTPException
from starlette import status


class NotFoundException(HTTPException):
    def __init__(self, detail=None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(HTTPException):
    def __init__(self, detail=None):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InternalServerError(HTTPException):
    def __init__(self, detail=None):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail=None):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(HTTPException):
    def __init__(self, detail=None):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

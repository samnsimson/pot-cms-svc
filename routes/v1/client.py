from fastapi import APIRouter
from starlette import status

router = APIRouter(prefix="/client", tags=['Client'])


@router.get("", status_code=status.HTTP_200_OK)
async def get():
    return {"response": ""}

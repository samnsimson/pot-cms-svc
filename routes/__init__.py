from fastapi import Depends, FastAPI
from routes.v1 import apps, auth
from config import config


def setup_v1_routes(app: FastAPI):
    app.include_router(auth.router)
    app.include_router(apps.router, dependencies=[Depends(config.AUTH_SCHEME)])

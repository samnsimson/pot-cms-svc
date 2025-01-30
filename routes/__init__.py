from fastapi import Depends, FastAPI
from routes.v1 import apps, auth, content, domain
from config import config


def setup_v1_routes(app: FastAPI):
    app.include_router(auth.router)
    app.include_router(apps.router, dependencies=[Depends(config.AUTH_SCHEME)])
    app.include_router(content.router, dependencies=[Depends(config.AUTH_SCHEME)])
    app.include_router(domain.router, dependencies=[Depends(config.AUTH_SCHEME)])

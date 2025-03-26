from fastapi import Depends, FastAPI
from routes.v1 import apps, auth, content, domain, media
from config import config

auth_dependency = Depends(config.AUTH_SCHEME)


def setup_v1_routes(app: FastAPI):
    app.include_router(auth.router)
    app.include_router(apps.router, dependencies=[auth_dependency])
    app.include_router(content.router, dependencies=[auth_dependency])
    app.include_router(domain.router, dependencies=[auth_dependency])
    app.include_router(media.router, dependencies=[auth_dependency])

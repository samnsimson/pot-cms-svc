from fastapi import FastAPI
from routes.v1 import auth, client
from dependencies import auth_dependency


def setup_v1_routes(app: FastAPI):
    app.include_router(auth.router)
    app.include_router(client.router, dependencies=[auth_dependency])

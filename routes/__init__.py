from fastapi import FastAPI
from routes.v1 import auth


def setup_v1_routes(app: FastAPI):
    app.include_router(auth.router)

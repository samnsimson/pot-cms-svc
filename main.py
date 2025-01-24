import uvicorn
from fastapi import FastAPI
from config import config
from contextlib import asynccontextmanager
from routes import setup_v1_routes

TITLE = config.PROJECT_NAME
DESCRIPTION = config.PROJECT_DESCRIPTION
VERSION = config.PROJECT_VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_v1_routes(app=app)
    yield


app = FastAPI(title=TITLE, description=DESCRIPTION, version=VERSION, root_path="/api/v1", lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)

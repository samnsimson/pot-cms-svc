import uvicorn
from fastapi import FastAPI
from config import config
from contextlib import asynccontextmanager
from database import init_db

TITLE = config.PROJECT_NAME
DESCRIPTION = config.PROJECT_DESCRIPTION
VERSION = config.PROJECT_VERSION


@asynccontextmanager
def lifecycle(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=TITLE, description=DESCRIPTION, version=VERSION, root_path="/api/v1")

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)

import uvicorn
from fastapi import FastAPI
from config import config
from contextlib import asynccontextmanager
from database import async_session
from routes import setup_v1_routes
from seed import seed_roles

TITLE = config.PROJECT_NAME
DESCRIPTION = config.PROJECT_DESCRIPTION
VERSION = config.PROJECT_VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_v1_routes(app)
    async with async_session() as session:
        await seed_roles(session)
    yield


app = FastAPI(title=TITLE, description=DESCRIPTION, version=VERSION, root_path="/api/v1", lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)

import uvicorn
from fastapi import FastAPI
from config import config
from contextlib import asynccontextmanager
from middleware.auth_middleware import AuthMiddleware
from fastapi.middleware.cors import CORSMiddleware
from routes import setup_v1_routes
from seed import seed_roles

TITLE = config.PROJECT_NAME
DESCRIPTION = config.PROJECT_DESCRIPTION
VERSION = config.PROJECT_VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    await seed_roles()
    yield


app = FastAPI(title=TITLE, description=DESCRIPTION, version=VERSION, root_path="/api/v1", lifespan=lifespan)

# MIDDLEWARES
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(AuthMiddleware)

# ROUTES
setup_v1_routes(app)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)

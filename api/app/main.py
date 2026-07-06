from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routes import auth, users, files, tokens, reviews, api_keys, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Openfield API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

health_router = APIRouter()


@health_router.get("/health")
async def health():
    return {"status": "ok", "version": "0.2.0"}


app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(tokens.router, prefix="/api/v1/tokens", tags=["tokens"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(api_keys.router, prefix="/api/v1/api-keys", tags=["api-keys"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

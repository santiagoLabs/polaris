from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.connection import db
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(
    title="Polaris",
    description="Multi-agent crisis response simulation",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Polaris API is running"}


@app.get("/health")
async def health_check():
    result = await db.fetchrow("SELECT 1 as status")
    return {
        "status": "healthy",
        "database": "connected" if result else "disconnected"
    }

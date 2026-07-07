from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app import models
from app.routers import auth, expenses, ocr
from app.config import settings

# Create tables in Database (Supabase PostgreSQL / Local SQLite)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finch Finance Backend API",
    description="Python FastAPI backend for Finch finance application",
    version="1.0.0"
)

# Configure CORS for frontend compatibility
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000",
]

if settings.ALLOWED_ORIGINS:
    extra_origins = [o.strip().rstrip("/") for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
    origins.extend(extra_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(ocr.router)

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "service": "Finch Finance Backend API"
    }

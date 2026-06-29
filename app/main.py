from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app import models
from app.routers import auth, expenses, ocr

# Create tables in Database (Supabase PostgreSQL / Local SQLite)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finch Finance Backend API",
    description="Python FastAPI backend for Finch finance application",
    version="1.0.0"
)

# Configure CORS for frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev/testing. Restrict in prod.
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

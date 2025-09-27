# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .controllers.api import router as api_router
from .controllers.auth import router as auth_router
from .models.db import Base, engine
from .tools.controller import router as tools_router
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Simple RAG FastAPI")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:3001",  # Alternative local port
        "https://legal-fa3mhai75-priyanshufoxs-projects.vercel.app",  # Your Vercel deployment
        "https://*.vercel.app",  # All Vercel apps
        "*"  # Allow all origins as fallback
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(api_router, prefix="/api", tags=["rag"])
app.include_router(tools_router, prefix="/api/tools", tags=["tools"])

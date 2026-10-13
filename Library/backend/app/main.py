from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.db.init_db import init_demo_catalogue
from app.api.v1.router import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("library_agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed demo catalog
    logger.info("Starting up AI Library Agent...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        init_demo_catalogue(db)
    finally:
        db.close()
    yield
    # Shutdown
    logger.info("Shutting down AI Library Agent...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent AI-powered Library Catalogue Assistant and Administration API.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred while processing your library request."}
    )

# Include v1 endpoints
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/api/v1/health", tags=["Health"])
def health_check():
    """Health check endpoint providing system status and AI provider readiness."""
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ai_provider_configured": settings.is_groq_configured(),
        "ai_model": settings.GROQ_MODEL if settings.is_groq_configured() else "offline-heuristic-mode"
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API.",
        "docs_url": "/docs",
        "health_url": "/api/v1/health"
    }

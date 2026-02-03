"""
AegisAI Backend Server - Updated CORS Configuration
Main entry point for the FastAPI application
"""

import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.settings import settings
from api.routes import router as api_router
from api.email_routes import email_router
from services.database_service import db_service
from utils.logger import setup_logging

# ----------------------------
# Setup Logging
# ----------------------------
setup_logging()
logger = logging.getLogger(__name__)

# ----------------------------
# Lifespan Handler (startup & shutdown)
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown tasks"""

    # ----------------------------
    # Startup logic
    # ----------------------------
    logger.info("=" * 60)
    logger.info("🛡️  AegisAI Backend Starting")
    logger.info("=" * 60)

    # Ensure evidence directory exists
    settings.EVIDENCE_DIR.mkdir(exist_ok=True, parents=True)

    # Database initialization
    logger.info(f"💾 Database: {settings.DB_PATH}")

    # Log configuration
    logger.info(f"📹 Video Source: {settings.VIDEO_SOURCE}")
    logger.info(f"⏱️  Frame Rate: Every {settings.FRAME_SAMPLE_RATE}s")
    logger.info(f"🤖 Model: {settings.GEMINI_MODEL}")
    logger.info(f"🌐 CORS Origins: {settings.CORS_ORIGINS}")
    logger.info("=" * 60)
    logger.info("✅ AegisAI Backend Ready")
    logger.info(f"🔗 API: http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"📖 Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    logger.info("=" * 60)

    yield  # Application runs here

    # ----------------------------
    # Shutdown logic
    # ----------------------------
    logger.info("🛑 AegisAI Backend Shutting Down")

    # Cleanup old incidents if configured
    if settings.MAX_EVIDENCE_AGE_DAYS:
        deleted = db_service.cleanup_old_incidents(settings.MAX_EVIDENCE_AGE_DAYS)
        logger.info(f"🧹 Cleaned up {deleted} old incidents")

    logger.info("👋 Goodbye!")


# ----------------------------
# FastAPI Application
# ----------------------------
app = FastAPI(
    title="AegisAI API",
    description="Autonomous Security & Incident Response Agent",
    version="2.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ----------------------------
# CORS Middleware - CRITICAL FIX
# ----------------------------
# Parse CORS origins from settings
cors_origins = settings.CORS_ORIGINS
if isinstance(cors_origins, str):
    # If it's a string representation of a list, parse it
    import json
    try:
        cors_origins = json.loads(cors_origins)
    except:
        cors_origins = [cors_origins]

logger.info(f"🔓 Configuring CORS for origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"], # Expose all headers
    max_age=3600,        # Cache preflight for 1 hour
)

# ----------------------------
# Exception Handler
# ----------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.LOG_LEVEL.upper() == "DEBUG" else None
        }
    )

# ----------------------------
# Include API Routes
# ----------------------------
app.include_router(api_router)

app.include_router(email_router)

# ----------------------------
# Root Endpoint
# ----------------------------
@app.get("/")
async def root():
    return {
        "name": "AegisAI",
        "version": "2.5.0",
        "status": "operational",
        "description": "Autonomous Security & Incident Response Agent",
        "docs": "/docs",
        "cors_configured": True,
        "allowed_origins": cors_origins
    }

# ----------------------------
# CORS Debug Endpoint
# ----------------------------
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle CORS preflight for all paths"""
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# ----------------------------
# Main Entry Point
# ----------------------------
if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 Starting Uvicorn server...")
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True if settings.LOG_LEVEL.upper() == "DEBUG" else False,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )

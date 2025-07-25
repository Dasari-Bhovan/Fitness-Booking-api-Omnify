"""
Main FastAPI application setup.
Configures the application, middleware, and route mounting.
"""

import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.routes.booking import router
from app.database.db_utils import create_tables, get_db
from app.services.booking import BookingService

from .config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="A comprehensive fitness studio booking API with timezone support",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/")
async def welcome():
    return {"success": True, "message": "Welcome to Fitness Booking API "}


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "details": {},
            "error_type": "internal_server_error",
        },
    )


# Include routers
app.include_router(router)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    try:
        # Create database tables
        create_tables()
        logger.info("Database tables created successfully")

        # Create sample data
        db = next(get_db())
        service = BookingService(db)
        service.create_sample_classes()
        logger.info("Sample data created successfully")

        logger.info(f"{settings.APP_NAME} v{settings.VERSION} started successfully")

    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info(f"{settings.APP_NAME} shutting down...")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

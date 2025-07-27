"""Main entry point for the Indian Constitution AI application."""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.logging import setup_logging

# Setup logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API router
app.include_router(api_router, prefix="/api/v1")

# Add exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."}
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Indian Constitution AI API",
        "docs_url": "/docs",
        "version": settings.PROJECT_VERSION
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Runs on application startup."""
    logger.info("Starting Indian Constitution AI API")
    
    # Ensure required directories exist
    os.makedirs(os.path.dirname(settings.VECTOR_STORE_PATH), exist_ok=True)
    
    # Check if OpenAI API key is set
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY environment variable not set. API may not function correctly.")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Runs on application shutdown."""
    logger.info("Shutting down Indian Constitution AI API")

if __name__ == "__main__":
    """This section will be executed when the script is run directly."""
    import uvicorn
    
    # Run the application with uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 
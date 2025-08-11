from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.logging import setup_logging, get_logger, PerformanceLogger
from app.services.cache_service import CacheService

# Global cache service instance
cache_service = None
performance_logger = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global cache_service, performance_logger
    
    # Startup
    logger = get_logger("app.startup")
    logger.info("Starting NLP Translation API")
    
    # Initialize cache service
    cache_service = CacheService(max_size=1000, ttl_seconds=3600)
    app.state.cache_service = cache_service
    logger.info("Cache service initialized")
    
    # Initialize performance logger
    performance_logger = PerformanceLogger()
    app.state.performance_logger = performance_logger
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NLP Translation API")
    if cache_service:
        await cache_service.clear()
    logger.info("Application shutdown complete")


# Initialize logging
setup_logging(
    log_level="DEBUG",
    structured_logging=True,
    console_logging=True
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-language translation API for Indian languages",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add performance monitoring middleware."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Add performance header
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log performance metrics
    if hasattr(app.state, 'performance_logger'):
        app.state.performance_logger.log_api_request(
            endpoint=str(request.url.path),
            method=request.method,
            response_time=process_time,
            status_code=response.status_code
        )
    
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger = get_logger("app.exceptions")
    logger.error(
        f"Unhandled exception in {request.method} {request.url.path}",
        exc_info=exc,
        extra={
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__
        }
    )


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "NLP Translation API",
        "version": settings.VERSION,
        "status": "healthy",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": f"{settings.API_V1_STR}/openapi.json"
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint."""
    logger = get_logger("app.health")
    
    # Check cache service
    cache_status = "healthy"
    cache_stats = {}
    try:
        if hasattr(app.state, 'cache_service'):
            cache_stats = await app.state.cache_service.get_stats()
    except Exception as e:
        logger.warning(f"Cache health check failed: {e}")
        cache_status = "degraded"
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "nlp-translation-api",
        "version": settings.VERSION,
        "services": {
            "cache": {
                "status": cache_status,
                "stats": cache_stats
            },
            "translation": {
                "status": "healthy",
                "available_models": ["mock_translator"]
            }
        }
    }
    
    return health_status

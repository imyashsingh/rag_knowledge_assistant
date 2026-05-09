import os
from app.api.rate_limiter import RateLimitMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from contextlib import asynccontextmanager
import time

from app.api.v1.router import api_router
from app.api.middleware import log_requests, jwt_auth_middleware
from app.db.base import Base
from app.db.session import engine
from app.core.redis_client import test_redis_connection
from app.core.exceptions import setup_exception_handlers
from app.config import settings

# Configure logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting RAG Knowledge Assistant API...")

    # Test Redis connection
    try:
        redis_healthy = test_redis_connection()
        if redis_healthy:
            logger.info("Redis connection successful")
        else:
            logger.warning(
                "Redis connection failed - caching will be disabled")
    except Exception as e:
        logger.warning(f"Redis connection test failed: {str(e)}")

    # Setup pgvector extension and indexes FIRST
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        logger.info("pgvector extension installed successfully")
    except Exception as e:
        logger.error(f"pgvector extension installation failed: {str(e)}")
        logger.error(
            "Please ensure pgvector extension is installed in PostgreSQL:")
        logger.error(
            "  - For Ubuntu/Debian: sudo apt-get install postgresql-<version>-pgvector")
        logger.error("  - For macOS: brew install pgvector")
        logger.error(
            "  - Or run: CREATE EXTENSION vector; in your database as superuser")
        raise

    # Create database tables AFTER pgvector extension
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database table creation failed: {str(e)}")
        raise

    # Setup vector indexes
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_chunks_embedding
                ON chunks USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """))
            conn.commit()
        logger.info("pgvector indexes setup complete")
    except Exception as e:
        logger.warning(f"Vector index creation failed: {str(e)}")
        logger.warning(
            "Application will continue without vector indexes (search may be slower)")

    logger.info("RAG Knowledge Assistant API startup complete")

    yield

    # Shutdown
    logger.info("Shutting down RAG Knowledge Assistant API...")


# Create FastAPI app
app = FastAPI(
    title="RAG Knowledge Assistant",
    description="RAG Knowledge Assistant API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router FIRST (before JWT middleware)
app.include_router(api_router, prefix="/api/v1")

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware, default_limit=100, default_window=60)

# Setup exception handlers
setup_exception_handlers(app)

# Add custom middleware AFTER router inclusion
app.middleware("http")(jwt_auth_middleware)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Knowledge Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.core.redis_client import RedisCache, test_redis_connection
from app.db.session import engine
from app.rag.llm import validate_api_key
from app.ingestion.processor import DocumentProcessor

router = APIRouter()


@router.get("/")
def health_check():
    """Comprehensive health check for all system components"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "components": {}
        }

        # Database health check
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
                health_status["components"]["database"] = {
                    "status": "healthy",
                    "message": "Database connection successful"
                }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }
            health_status["status"] = "degraded"

        # Redis health check
        try:
            redis_healthy = test_redis_connection()
            if redis_healthy:
                health_status["components"]["redis"] = {
                    "status": "healthy",
                    "message": "Redis connection successful"
                }
            else:
                health_status["components"]["redis"] = {
                    "status": "unhealthy",
                    "message": "Redis connection failed"
                }
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["redis"] = {
                "status": "unhealthy",
                "message": f"Redis check failed: {str(e)}"
            }
            health_status["status"] = "degraded"

        # Groq API health check
        try:
            groq_healthy = validate_api_key()
            if groq_healthy:
                health_status["components"]["groq"] = {
                    "status": "healthy",
                    "message": "Groq API connection successful"
                }
            else:
                health_status["components"]["groq"] = {
                    "status": "unhealthy",
                    "message": "Groq API connection failed"
                }
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["groq"] = {
                "status": "unhealthy",
                "message": f"Groq API check failed: {str(e)}"
            }
            health_status["status"] = "degraded"

        # Document processor health check
        try:
            processor = DocumentProcessor()
            supported_extensions = processor.get_supported_extensions()
            health_status["components"]["document_processor"] = {
                "status": "healthy",
                "message": f"Document processor ready, supports: {', '.join(supported_extensions)}"
            }
        except Exception as e:
            health_status["components"]["document_processor"] = {
                "status": "unhealthy",
                "message": f"Document processor failed: {str(e)}"
            }
            health_status["status"] = "degraded"

        # Cache statistics
        try:
            cache_stats = RedisCache.get_cache_stats()
            health_status["components"]["cache"] = {
                "status": "healthy",
                "message": "Cache operational",
                "stats": cache_stats
            }
        except Exception as e:
            health_status["components"]["cache"] = {
                "status": "unhealthy",
                "message": f"Cache check failed: {str(e)}"
            }
            health_status["status"] = "degraded"

        return health_status

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/simple")
def simple_health():
    """Simple health check for load balancers"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.get("/ready")
def readiness_check():
    """Readiness check for Kubernetes"""
    try:
        # Check critical components
        redis_healthy = test_redis_connection()
        groq_healthy = validate_api_key()

        if redis_healthy and groq_healthy:
            return {"status": "ready"}
        else:
            return {"status": "not_ready", "redis": redis_healthy, "groq": groq_healthy}

    except Exception as e:
        return {"status": "not_ready", "error": str(e)}


@router.get("/live")
def liveness_check():
    """Liveness check for Kubernetes"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}

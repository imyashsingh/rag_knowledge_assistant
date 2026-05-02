#!/usr/bin/env python3
"""
Health check script for DocuMind backend
"""

import os
import sys
import time
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from app.core.redis_client import test_redis_connection, RedisCache
from app.db.session import engine
from app.rag.llm import validate_api_key
from app.utils.logger import setup_logging, get_logger


def check_database():
    """Check database connection and basic functionality"""
    logger = get_logger(__name__)
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            result.fetchone()
        
        # Test pgvector extension
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            if not result.fetchone():
                raise Exception("pgvector extension not found")
        
        # Test basic query
        with engine.connect() as conn:
            result = conn.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            table_count = result.fetchone()[0]
        
        logger.info(f"✅ Database: Connected ({table_count} tables found)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database: {str(e)}")
        return False


def check_redis():
    """Check Redis connection and basic functionality"""
    logger = get_logger(__name__)
    
    try:
        # Test connection
        if not test_redis_connection():
            raise Exception("Connection failed")
        
        # Test basic operations
        test_key = "health_check_test"
        test_value = "test_value"
        
        # Test set/get
        if not RedisCache.set(test_key, test_value, ex=10):
            raise Exception("Set operation failed")
        
        retrieved = RedisCache.get(test_key)
        if retrieved != test_value:
            raise Exception("Get operation failed")
        
        # Clean up
        RedisCache.delete(test_key)
        
        # Get cache stats
        stats = RedisCache.get_cache_stats()
        
        logger.info(f"✅ Redis: Connected (clients: {stats.get('connected_clients', 0)}, memory: {stats.get('used_memory', 'N/A')})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Redis: {str(e)}")
        return False


def check_groq_api():
    """Check Groq API connection"""
    logger = get_logger(__name__)
    
    try:
        if not validate_api_key():
            raise Exception("API key validation failed")
        
        logger.info("✅ Groq API: Connected")
        return True
        
    except Exception as e:
        logger.error(f"❌ Groq API: {str(e)}")
        return False


def check_embeddings():
    """Check embedding generation functionality"""
    logger = get_logger(__name__)
    
    try:
        from app.rag.embeddings import generate_embedding
        
        test_text = "This is a test text for embedding generation."
        embedding = generate_embedding(test_text)
        
        if not embedding or len(embedding) == 0:
            raise Exception("Embedding generation failed")
        
        logger.info(f"✅ Embeddings: Working (dimension: {len(embedding)})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Embeddings: {str(e)}")
        return False


def check_file_processing():
    """Check document processing functionality"""
    logger = get_logger(__name__)
    
    try:
        from app.ingestion.processor import DocumentProcessor
        
        processor = DocumentProcessor()
        extensions = processor.get_supported_extensions()
        
        if not extensions:
            raise Exception("No supported file extensions found")
        
        logger.info(f"✅ File Processing: Working (supports: {', '.join(extensions)})")
        return True
        
    except Exception as e:
        logger.error(f"❌ File Processing: {str(e)}")
        return False


def check_environment():
    """Check environment variables"""
    logger = get_logger(__name__)
    
    required_vars = ["DB_URL", "JWT_SECRET", "GROQ_API_KEY", "REDIS_HOST", "REDIS_PASSWORD"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Environment: Missing variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("✅ Environment: All required variables set")
    return True


def run_health_check(detailed: bool = False):
    """Run comprehensive health check"""
    logger = get_logger(__name__)
    
    logger.info("Starting comprehensive health check...")
    
    checks = [
        ("Environment", check_environment),
        ("Database", check_database),
        ("Redis", check_redis),
        ("Groq API", check_groq_api),
        ("Embeddings", check_embeddings),
        ("File Processing", check_file_processing),
    ]
    
    results = {}
    start_time = time.time()
    
    for name, check_func in checks:
        if detailed:
            logger.info(f"Checking {name}...")
        
        results[name] = check_func()
        
        if detailed:
            time.sleep(0.1)  # Small delay between checks
    
    end_time = time.time()
    duration = (end_time - start_time) * 1000
    
    # Summary
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    logger.info(f"\n=== Health Check Summary ===")
    logger.info(f"Duration: {duration:.2f}ms")
    logger.info(f"Results: {passed}/{total} checks passed")
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {name}: {status}")
    
    if passed == total:
        logger.info("🎉 All systems operational!")
        return True
    else:
        logger.warning(f"⚠️  {total - passed} system(s) have issues")
        return False


def run_quick_check():
    """Run quick health check (database and redis only)"""
    logger = get_logger(__name__)
    
    logger.info("Running quick health check...")
    
    db_ok = check_database()
    redis_ok = check_redis()
    
    if db_ok and redis_ok:
        logger.info("✅ Quick check passed")
        return True
    else:
        logger.error("❌ Quick check failed")
        return False


if __name__ == "__main__":
    # Setup logging
    setup_logging(log_level="INFO")
    
    logger = get_logger(__name__)
    
    # Check command line arguments
    detailed = "--detailed" in sys.argv or "-d" in sys.argv
    quick = "--quick" in sys.argv or "-q" in sys.argv
    
    if quick:
        success = run_quick_check()
    else:
        success = run_health_check(detailed=detailed)
    
    sys.exit(0 if success else 1)

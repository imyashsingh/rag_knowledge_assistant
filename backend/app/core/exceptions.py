from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import time

logger = logging.getLogger(__name__)


class DocuMindException(Exception):
    """Base exception for DocuMind application"""

    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class DatabaseException(DocuMindException):
    """Database related exceptions"""
    pass


class RedisException(DocuMindException):
    """Redis related exceptions"""
    pass


class EmbeddingException(DocuMindException):
    """Embedding generation exceptions"""
    pass


class RAGException(DocuMindException):
    """RAG pipeline exceptions"""
    pass


class AuthenticationException(DocuMindException):
    """Authentication related exceptions"""
    pass


class DocumentProcessingException(DocuMindException):
    """Document processing exceptions"""
    pass


class ValidationException(DocuMindException):
    """Validation exceptions"""
    pass


async def documind_exception_handler(request: Request, exc: DocuMindException):
    """Handler for custom DocuMind exceptions"""
    logger.error(f"DocuMind exception: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": exc.message,
            "error_code": exc.error_code,
            "timestamp": time.time()
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for request validation exceptions"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": exc.errors(),
            "timestamp": time.time()
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler for HTTP exceptions"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "message": exc.detail,
            "timestamp": time.time()
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handler for general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": time.time()
        }
    )


def setup_exception_handlers(app: FastAPI):
    """Setup all exception handlers for the FastAPI app"""
    app.add_exception_handler(DocuMindException, documind_exception_handler)
    app.add_exception_handler(RequestValidationError,
                              validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

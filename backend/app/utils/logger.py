"""
Logging configuration for DocuMind backend
"""

import logging
import logging.handlers
import os
import uuid
from typing import Optional
from datetime import datetime


class RequestIDFilter(logging.Filter):
    """Filter to add request ID to log records"""
    
    def filter(self, record):
        # Generate or get request ID from context
        if not hasattr(record, 'request_id'):
            record.request_id = getattr(record, 'request_id', 'no-request-id')
        return True


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add request ID if available
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        
        # Add exception info if available
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created', 'msecs',
                          'relativeCreated', 'thread', 'threadName', 'processName',
                          'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                log_data[key] = value
        
        return str(log_data)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_structured: bool = True,
    enable_file_rotation: bool = True
) -> None:
    """
    Setup application logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        enable_structured: Enable structured JSON logging
        enable_file_rotation: Enable log file rotation
    """
    # Get log level from environment or parameter
    log_level = os.getenv("LOG_LEVEL", log_level).upper()
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))
    
    if enable_structured:
        console_formatter = StructuredFormatter()
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(RequestIDFilter())
    root_logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        if enable_file_rotation:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
        else:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
        
        file_handler.setLevel(logging.DEBUG)  # Always DEBUG for files
        
        if enable_structured:
            file_formatter = StructuredFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
        
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(RequestIDFilter())
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('uvicorn.access').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('redis').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_request_start(logger: logging.Logger, method: str, path: str, request_id: str = None):
    """
    Log the start of a request
    
    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        request_id: Request ID for tracing
    """
    extra = {'request_id': request_id or str(uuid.uuid4())}
    logger.info(f"Request started: {method} {path}", extra=extra)


def log_request_end(
    logger: logging.Logger, 
    method: str, 
    path: str, 
    status_code: int, 
    duration_ms: float,
    request_id: str = None
):
    """
    Log the end of a request
    
    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        request_id: Request ID for tracing
    """
    extra = {'request_id': request_id, 'status_code': status_code, 'duration_ms': duration_ms}
    logger.info(f"Request completed: {method} {path} - {status_code} ({duration_ms:.2f}ms)", extra=extra)


def log_error(
    logger: logging.Logger, 
    error: Exception, 
    context: str = None,
    request_id: str = None,
    user_id: int = None
):
    """
    Log an error with context information
    
    Args:
        logger: Logger instance
        error: Exception to log
        context: Context description
        request_id: Request ID for tracing
        user_id: User ID for context
    """
    extra = {
        'request_id': request_id,
        'user_id': user_id,
        'error_type': type(error).__name__,
        'error_message': str(error)
    }
    
    message = f"Error in {context}: {type(error).__name__}: {str(error)}" if context else f"Error: {type(error).__name__}: {str(error)}"
    
    logger.error(message, exc_info=True, extra=extra)


def log_performance(
    logger: logging.Logger,
    operation: str,
    duration_ms: float,
    details: dict = None,
    request_id: str = None
):
    """
    Log performance metrics
    
    Args:
        logger: Logger instance
        operation: Operation name
        duration_ms: Duration in milliseconds
        details: Additional performance details
        request_id: Request ID for tracing
    """
    extra = {
        'request_id': request_id,
        'operation': operation,
        'duration_ms': duration_ms,
        'details': details or {}
    }
    
    logger.info(f"Performance: {operation} completed in {duration_ms:.2f}ms", extra=extra)


def configure_request_logging():
    """Configure request/response logging middleware"""
    # This would be used with FastAPI middleware
    from fastapi import Request, Response
    import time
    
    async def log_requests_responses(request: Request, call_next):
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Log request start
        logger = get_logger("request")
        log_request_start(
            logger, 
            request.method, 
            str(request.url.path), 
            request_id
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log request completion
        log_request_end(
            logger,
            request.method,
            str(request.url.path),
            response.status_code,
            duration_ms,
            request_id
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    return log_requests_responses

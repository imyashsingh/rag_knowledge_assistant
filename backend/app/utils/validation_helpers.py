"""
Validation utilities for DocuMind backend
"""

import re
from typing import Optional, Any


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> dict:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        Dictionary with validation result and errors
    """
    errors = []
    
    if not password:
        errors.append("Password is required")
        return {"valid": False, "errors": errors}
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if len(password) > 128:
        errors.append("Password must be less than 128 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return {"valid": len(errors) == 0, "errors": errors}


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Truncate to max length
    text = text[:max_length]
    
    return text.strip()


def validate_workspace_name(name: str) -> dict:
    """
    Validate workspace name
    
    Args:
        name: Workspace name to validate
        
    Returns:
        Dictionary with validation result and errors
    """
    errors = []
    
    if not name:
        errors.append("Workspace name is required")
        return {"valid": False, "errors": errors}
    
    if len(name) < 2:
        errors.append("Workspace name must be at least 2 characters long")
    
    if len(name) > 100:
        errors.append("Workspace name must be less than 100 characters long")
    
    # Check for invalid characters
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        errors.append("Workspace name can only contain letters, numbers, spaces, hyphens, and underscores")
    
    return {"valid": len(errors) == 0, "errors": errors}


def validate_document_title(title: str) -> dict:
    """
    Validate document title
    
    Args:
        title: Document title to validate
        
    Returns:
        Dictionary with validation result and errors
    """
    errors = []
    
    if not title:
        errors.append("Document title is required")
        return {"valid": False, "errors": errors}
    
    if len(title) < 1:
        errors.append("Document title must be at least 1 character long")
    
    if len(title) > 255:
        errors.append("Document title must be less than 255 characters long")
    
    return {"valid": len(errors) == 0, "errors": errors}


def validate_query(query: str) -> dict:
    """
    Validate search query
    
    Args:
        query: Search query to validate
        
    Returns:
        Dictionary with validation result and errors
    """
    errors = []
    
    if not query:
        errors.append("Query is required")
        return {"valid": False, "errors": errors}
    
    if len(query.strip()) == 0:
        errors.append("Query cannot be empty")
    
    if len(query) > 1000:
        errors.append("Query must be less than 1000 characters long")
    
    return {"valid": len(errors) == 0, "errors": errors}


def validate_page_number(page: int, total_pages: int) -> dict:
    """
    Validate page number for pagination
    
    Args:
        page: Page number
        total_pages: Total number of pages
        
    Returns:
        Dictionary with validation result and errors
    """
    errors = []
    
    if page < 1:
        errors.append("Page number must be at least 1")
    
    if total_pages > 0 and page > total_pages:
        errors.append(f"Page number cannot exceed {total_pages}")
    
    return {"valid": len(errors) == 0, "errors": errors}


def validate_limit(limit: int, max_limit: int = 100) -> dict:
    """
    Validate limit for pagination
    
    Args:
        limit: Limit value
        max_limit: Maximum allowed limit
        
    Returns:
        Dictionary with validation result and errors
    """
    errors = []
    
    if limit < 1:
        errors.append("Limit must be at least 1")
    
    if limit > max_limit:
        errors.append(f"Limit cannot exceed {max_limit}")
    
    return {"valid": len(errors) == 0, "errors": errors}


def is_safe_string(value: Any) -> bool:
    """
    Check if value is a safe string (no SQL injection patterns)
    
    Args:
        value: Value to check
        
    Returns:
        True if safe, False otherwise
    """
    if not isinstance(value, str):
        return False
    
    # Check for common SQL injection patterns
    sql_patterns = [
        r'(?i)\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b',
        r'(?i)(--|#|/\*|\*/)',
        r'(?i)(or|and)\s+\d+\s*=\s*\d+',
        r'(?i)(or|and)\s+\'\w+\'\s*=\s*\'\w+\'',
        r'(?i)(\'|").*?(\'|").*?(\'|")',
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, value):
            return False
    
    return True

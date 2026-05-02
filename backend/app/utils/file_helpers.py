"""
File processing utilities for DocuMind backend
"""

import os
from pathlib import Path
from typing import Optional


SUPPORTED_EXTENSIONS = {
    '.txt', '.pdf', '.docx', '.md', '.markdown'
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension (including dot)
    """
    return Path(filename).suffix.lower()


def is_supported_file_type(filename: str) -> bool:
    """
    Check if file type is supported
    
    Args:
        filename: Name of the file
        
    Returns:
        True if supported, False otherwise
    """
    extension = get_file_extension(filename)
    return extension in SUPPORTED_EXTENSIONS


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def validate_file_size(file_size: int, max_size: int = MAX_FILE_SIZE) -> bool:
    """
    Validate file size against maximum allowed size
    
    Args:
        file_size: File size in bytes
        max_size: Maximum allowed size in bytes
        
    Returns:
        True if valid, False otherwise
    """
    return 0 < file_size <= max_size


def get_content_type(filename: str) -> str:
    """
    Get MIME content type based on file extension
    
    Args:
        filename: Name of the file
        
    Returns:
        MIME content type
    """
    extension = get_file_extension(filename)
    
    content_types = {
        '.txt': 'text/plain',
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.md': 'text/markdown',
        '.markdown': 'text/markdown'
    }
    
    return content_types.get(extension, 'application/octet-stream')


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory_path: Path to directory
        
    Returns:
        True if directory exists or was created
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False


def safe_filename(filename: str) -> str:
    """
    Generate a safe filename by removing/replacing problematic characters
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Remove problematic characters
    safe_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    
    # Keep only safe characters
    safe_name = ''.join(c for c in filename if c in safe_chars)
    
    # Replace spaces with underscores
    safe_name = safe_name.replace(' ', '_')
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = 'unnamed_file'
    
    return safe_name


def get_unique_filename(directory: str, filename: str) -> str:
    """
    Generate a unique filename in the specified directory
    
    Args:
        directory: Directory path
        filename: Original filename
        
    Returns:
        Unique filename
    """
    path = Path(directory) / filename
    
    if not path.exists():
        return filename
    
    # Add counter to make unique
    stem = path.stem
    suffix = path.suffix
    counter = 1
    
    while True:
        new_filename = f"{stem}_{counter}{suffix}"
        new_path = Path(directory) / new_filename
        
        if not new_path.exists():
            return new_filename
        
        counter += 1


def is_text_file(filename: str) -> bool:
    """
    Check if file is a text file
    
    Args:
        filename: Name of the file
        
    Returns:
        True if text file, False otherwise
    """
    text_extensions = {'.txt', '.md', '.markdown'}
    return get_file_extension(filename) in text_extensions


def is_document_file(filename: str) -> bool:
    """
    Check if file is a document file (PDF, DOCX)
    
    Args:
        filename: Name of the file
        
    Returns:
        True if document file, False otherwise
    """
    doc_extensions = {'.pdf', '.docx'}
    return get_file_extension(filename) in doc_extensions

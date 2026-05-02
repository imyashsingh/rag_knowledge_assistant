"""
Formatting utilities for DocuMind backend
"""

import datetime
from typing import Union


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def format_date(date: Union[datetime.datetime, datetime.date, str], format_type: str = "iso") -> str:
    """
    Format date in various formats
    
    Args:
        date: Date to format
        format_type: Format type ("iso", "readable", "short")
        
    Returns:
        Formatted date string
    """
    if isinstance(date, str):
        try:
            date = datetime.datetime.fromisoformat(date.replace('Z', '+00:00'))
        except ValueError:
            return date
    
    if isinstance(date, datetime.date) and not isinstance(date, datetime.datetime):
        date = datetime.datetime.combine(date, datetime.time.min)
    
    if format_type == "iso":
        return date.isoformat()
    elif format_type == "readable":
        return date.strftime("%B %d, %Y at %I:%M %p")
    elif format_type == "short":
        return date.strftime("%m/%d/%Y %H:%M")
    else:
        return date.isoformat()


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}h {remaining_minutes}m"


def format_number(number: Union[int, float], precision: int = 2) -> str:
    """
    Format number with thousands separator
    
    Args:
        number: Number to format
        precision: Decimal precision
        
    Returns:
        Formatted number string
    """
    if isinstance(number, float):
        return f"{number:,.{precision}f}"
    else:
        return f"{number:,}"


def format_percentage(value: float, precision: int = 1) -> str:
    """
    Format value as percentage
    
    Args:
        value: Value (0-1)
        precision: Decimal precision
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{precision}f}%"


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to specified length
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_list(items: list, conjunction: str = "and") -> str:
    """
    Format list as readable string
    
    Args:
        items: List of items
        conjunction: Conjunction to use
        
    Returns:
        Formatted string
    """
    if not items:
        return ""
    elif len(items) == 1:
        return str(items[0])
    elif len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    else:
        return f"{', '.join(map(str, items[:-1]))}, {conjunction} {items[-1]}"


def pluralize(count: int, singular: str, plural: str = None) -> str:
    """
    Return singular or plural form based on count
    
    Args:
        count: Number of items
        singular: Singular form
        plural: Plural form (if None, adds 's' to singular)
        
    Returns:
        Appropriate form
    """
    if count == 1:
        return singular
    
    if plural is None:
        plural = singular + "s"
    
    return plural

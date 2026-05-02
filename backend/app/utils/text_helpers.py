"""
Text processing utilities for DocuMind backend
"""

import re
from typing import List, Optional


def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\\]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text using simple frequency analysis
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Simple keyword extraction based on word frequency
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter out common words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
        'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
        'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all',
        'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such'
    }
    
    # Count word frequencies
    word_freq = {}
    for word in words:
        if len(word) > 2 and word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, freq in sorted_words[:max_keywords]]


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences
    
    Args:
        text: Text to split
        
    Returns:
        List of sentences
    """
    if not text:
        return []
    
    # Simple sentence splitting
    sentences = re.split(r'[.!?]+', text)
    
    # Clean and filter empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences


def count_words(text: str) -> int:
    """
    Count words in text
    
    Args:
        text: Text to count words in
        
    Returns:
        Word count
    """
    if not text:
        return 0
    
    words = re.findall(r'\b\w+\b', text)
    return len(words)


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Estimate reading time in minutes
    
    Args:
        text: Text to calculate reading time for
        words_per_minute: Average reading speed
        
    Returns:
        Estimated reading time in minutes
    """
    word_count = count_words(text)
    return max(1, round(word_count / words_per_minute))

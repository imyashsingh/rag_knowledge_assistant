from typing import List
from app.ingestion.chunkers.base_chunker import BaseChunker


class FixedChunker(BaseChunker):
    """Fixed-size text chunker with overlap"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into fixed-size chunks with overlap"""
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If this is the last chunk, take whatever remains
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to break at a sentence or word boundary
            chunk = text[start:end]
            
            # Look for sentence boundaries (., !, ?)
            sentence_end = max(
                chunk.rfind('.'),
                chunk.rfind('!'),
                chunk.rfind('?')
            )
            
            if sentence_end > self.chunk_size * 0.7:  # Only use sentence break if it's not too early
                chunk = chunk[:sentence_end + 1]
                end = start + len(chunk)
            else:
                # Look for word boundaries (space, newline)
                word_end = chunk.rfind(' ')
                if word_end > self.chunk_size * 0.8:
                    chunk = chunk[:word_end]
                    end = start + len(chunk)
            
            chunks.append(chunk.strip())
            start = end - self.overlap
        
        return [chunk for chunk in chunks if chunk.strip()]

from typing import List
from app.ingestion.chunkers.base_chunker import BaseChunker

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class SemanticChunker(BaseChunker):
    """Semantic chunker using LangChain's RecursiveCharacterTextSplitter"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is required for semantic chunking. Install with: pip install langchain")
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into semantic chunks"""
        if not text:
            return []
        
        try:
            chunks = self.splitter.split_text(text)
            return [chunk.strip() for chunk in chunks if chunk.strip()]
        except Exception as e:
            print(f"Error in semantic chunking: {str(e)}")
            # Fallback to simple splitting
            return [text[i:i+500] for i in range(0, len(text), 450)]

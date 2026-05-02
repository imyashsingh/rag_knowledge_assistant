from typing import List, Optional
import os
from pathlib import Path
from app.ingestion.parsers.pdf_parser import PDFParser
from app.ingestion.parsers.txt_parser import TextParser
from app.ingestion.parsers.docx_parser import DocxParser
from app.ingestion.chunkers.fixed_chunker import FixedChunker
from app.ingestion.chunkers.semantic_chunker import SemanticChunker
from app.rag.embeddings import generate_embeddings
from app.db.session import SessionLocal
from app.db.repositories.document_repo import DocumentRepository
from app.db.repositories.chunk_repo import ChunkRepository


class DocumentProcessor:
    """Main document processor for ingestion pipeline"""
    
    def __init__(self, use_semantic_chunking: bool = False):
        # Initialize parsers
        self.parsers = [
            PDFParser(),
            TextParser(),
            DocxParser()
        ]
        
        # Initialize chunker
        if use_semantic_chunking:
            self.chunker = SemanticChunker(chunk_size=500, chunk_overlap=50)
        else:
            self.chunker = FixedChunker(chunk_size=500, overlap=50)
    
    def get_parser_for_file(self, filename: str) -> Optional[object]:
        """Get appropriate parser for file type"""
        for parser in self.parsers:
            if parser.can_parse(filename):
                return parser
        return None
    
    def process_document(
        self, 
        file_path: str, 
        title: str,
        workspace_id: int
    ) -> Optional[int]:
        """
        Process a document: parse, chunk, generate embeddings, and store in database
        
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Get file info
            filename = Path(file_path).name
            content_type = self._get_content_type(filename)
            
            # Parse document
            parser = self.get_parser_for_file(filename)
            if not parser:
                raise ValueError(f"No parser available for file: {filename}")
            
            text_content = parser.parse(file_path)
            if not text_content:
                raise ValueError(f"Failed to parse document: {filename}")
            
            # Store in database
            db = SessionLocal()
            try:
                doc_repo = DocumentRepository(db)
                chunk_repo = ChunkRepository(db)
                
                # Create document record
                document = doc_repo.create_document(
                    title=title,
                    filename=filename,
                    content_type=content_type,
                    workspace_id=workspace_id
                )
                
                # Chunk text
                chunks = self.chunker.chunk_text(text_content)
                
                # Generate embeddings for chunks
                embeddings = generate_embeddings(chunks)
                
                # Store chunks with embeddings
                for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                    chunk_repo.create_chunk(
                        text=chunk_text,
                        embedding=embedding,
                        workspace_id=workspace_id,
                        document_id=document.id,
                        chunk_index=i
                    )
                
                return document.id
                
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error processing document {file_path}: {str(e)}")
            return None
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type based on file extension"""
        ext = Path(filename).suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.markdown': 'text/markdown',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword'
        }
        return content_types.get(ext, 'application/octet-stream')
    
    def get_supported_extensions(self) -> List[str]:
        """Get all supported file extensions"""
        extensions = []
        for parser in self.parsers:
            extensions.extend(parser.get_supported_extensions())
        return list(set(extensions))

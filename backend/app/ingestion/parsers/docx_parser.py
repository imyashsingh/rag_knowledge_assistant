from typing import Optional
from app.ingestion.parsers.base_parser import BaseParser

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class DocxParser(BaseParser):
    """Parser for DOCX files"""
    
    def parse(self, file_path: str) -> Optional[str]:
        """Parse DOCX file and return text content"""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx is required for DOCX parsing. Install with: pip install python-docx")
        
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error parsing DOCX file {file_path}: {str(e)}")
            return None
    
    def get_supported_extensions(self) -> list[str]:
        return ['.docx', '.doc']

from typing import Optional
from app.ingestion.parsers.base_parser import BaseParser

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


class PDFParser(BaseParser):
    """Parser for PDF files"""
    
    def parse(self, file_path: str) -> Optional[str]:
        """Parse PDF file and return text content"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 is required for PDF parsing. Install with: pip install PyPDF2")
        
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error parsing PDF file {file_path}: {str(e)}")
            return None
    
    def get_supported_extensions(self) -> list[str]:
        return ['.pdf']

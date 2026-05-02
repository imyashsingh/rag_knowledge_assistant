from typing import Optional
from app.ingestion.parsers.base_parser import BaseParser


class TextParser(BaseParser):
    """Parser for plain text files"""
    
    def parse(self, file_path: str) -> Optional[str]:
        """Parse text file and return content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error parsing text file {file_path}: {str(e)}")
            return None
    
    def get_supported_extensions(self) -> list[str]:
        return ['.txt', '.text', '.md', '.markdown']

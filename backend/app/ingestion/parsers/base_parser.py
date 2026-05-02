from abc import ABC, abstractmethod
from typing import Optional


class BaseParser(ABC):
    """Base class for document parsers"""
    
    @abstractmethod
    def parse(self, file_path: str) -> Optional[str]:
        """Parse document and return text content"""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> list[str]:
        """Return list of supported file extensions"""
        pass
    
    def can_parse(self, filename: str) -> bool:
        """Check if parser can handle the given file"""
        return any(filename.lower().endswith(ext) for ext in self.get_supported_extensions())

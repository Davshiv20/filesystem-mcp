from pathlib import Path
from typing import List
from ..config import Settings

settings = Settings()


def validate_file_extension(filename: str) -> bool:
    """Validate if file extension is allowed"""
    if not filename:
        return False
    
    file_path = Path(filename)
    extension = file_path.suffix.lower()
    
    return extension in settings.allowed_file_extensions


def validate_file_size(file_size_bytes: int) -> bool:
    """Validate if file size is within limits"""
    max_size_bytes = settings.max_file_size_mb * 1024 * 1024
    return file_size_bytes <= max_size_bytes 
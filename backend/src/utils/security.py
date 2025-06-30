import re
from pathlib import Path
from typing import Optional


def sanitize_path(path: str) -> Optional[str]:
    """Sanitize and validate file path"""
    if not path:
        return None
    
    # Remove any null bytes
    path = path.replace('\x00', '')
    
    # Normalize path separators
    path = path.replace('\\', '/')
    
    # Remove leading/trailing slashes
    path = path.strip('/')
    
    # Check for path traversal attempts
    if '..' in path or path.startswith('/') or path.startswith('~'):
        return None
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'^[a-zA-Z]:',  # Windows drive letters
        r'^//',         # Network paths
        r'^\\\\',       # Windows network paths
    ]
    
    for pattern in suspicious_patterns:
        if re.match(pattern, path):
            return None
    
    return path


def is_safe_path(base_path: Path, target_path: Path) -> bool:
    """Check if target path is within base path (prevents path traversal)"""
    try:
        base_resolved = base_path.resolve()
        target_resolved = target_path.resolve()
        
        # Check if target is within base
        return str(target_resolved).startswith(str(base_resolved))
    except (ValueError, RuntimeError):
        return False 
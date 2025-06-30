from .file_system_service import FileSystemService
from ..config import Settings

settings = Settings()
file_system_service = FileSystemService(settings.workspaces_dir) 
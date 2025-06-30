from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    app_name: str = "Filesystem MCP Server"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS settings
    allowed_origins: List[str] = ["*"]
    
    # File system settings
    workspaces_dir: str = "workspaces"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = [
        ".txt", ".md", ".py", ".js", ".html", ".css", ".json", 
        ".xml", ".yaml", ".yml", ".csv", ".log", ".pdf", ".doc", ".docx"
    ]
    
    
    together_api_key: str = ""
    llm_model: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free" 
    llm_temperature: float = 0.7
    llm_max_tokens: int = 512
    llm_timeout: int = 30
    
    # Security settings
    max_workspace_size: int = 1024 * 1024 * 1024  # 1GB
    max_files_per_workspace: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = False 
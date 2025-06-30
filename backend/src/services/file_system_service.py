import os
import shutil
import aiofiles
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..models import FileOperation, FileInfo, WorkspaceInfo, FileOperationType

# Configure logging
logger = logging.getLogger(__name__)

class FileSystemService:
    """Service for handling file system operations"""
    
    def __init__(self, base_workspace_dir: str = "workspaces"):
        self.base_workspace_dir = Path(base_workspace_dir)
        self.base_workspace_dir.mkdir(exist_ok=True)
        self.workspaces: Dict[str, WorkspaceInfo] = {}
        logger.info(f"FileSystemService initialized with base directory: {self.base_workspace_dir.absolute()}")
    
    def get_workspace_path(self, workspace_id: str) -> Path:
        """Get the absolute path for a workspace"""
        workspace_path = self.base_workspace_dir / workspace_id
        logger.info(f"Getting workspace path for {workspace_id}: {workspace_path.absolute()}")
        return workspace_path
    
    def create_workspace(self, name: str) -> WorkspaceInfo:
        """Create a new workspace"""
        workspace_id = str(uuid.uuid4())
        workspace_path = self.get_workspace_path(workspace_id)
        workspace_path.mkdir(exist_ok=True)
        logger.info(f"Created workspace directory: {workspace_path.absolute()}")
        
        workspace_info = WorkspaceInfo(
            workspace_id=workspace_id,
            name=name,
            path=str(workspace_path),
            file_count=0,
            created_at=datetime.now().isoformat()
        )
        
        self.workspaces[workspace_id] = workspace_info
        logger.info(f"Added workspace to memory: {workspace_id}")
        return workspace_info
    
    def get_workspace_info(self, workspace_id: str) -> Optional[WorkspaceInfo]:
        """Get workspace information"""
        return self.workspaces.get(workspace_id)
    
    def validate_workspace_path(self, workspace_id: str, file_path: str) -> Path:
        """Validate and return safe file path within workspace"""
        workspace_path = self.get_workspace_path(workspace_id)
        if not workspace_path.exists():
            raise ValueError(f"Workspace {workspace_id} does not exist")
        
        # Resolve the full path and ensure it's within the workspace
        full_path = (workspace_path / file_path).resolve()
        if not str(full_path).startswith(str(workspace_path.resolve())):
            raise ValueError("Path traversal detected")
        
        return full_path
    
    async def create_file(self, workspace_id: str, file_path: str, content: str) -> Dict[str, Any]:
        """Create a new file"""
        try:
            logger.info(f"Creating file: {file_path} in workspace: {workspace_id}")
            full_path = self.validate_workspace_path(workspace_id, file_path)
            logger.info(f"Full path for file: {full_path.absolute()}")
            
            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured parent directory exists: {full_path.parent.absolute()}")
            
            async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            logger.info(f"File created successfully: {full_path.absolute()}")
            logger.info(f"File exists after creation: {full_path.exists()}")
            
            return {
                "operation": "create",
                "path": file_path,
                "success": True,
                "message": f"File {file_path} created successfully"
            }
        except Exception as e:
            logger.error(f"Failed to create file {file_path}: {str(e)}")
            return {
                "operation": "create",
                "path": file_path,
                "success": False,
                "message": f"Failed to create file: {str(e)}"
            }
    
    async def edit_file(self, workspace_id: str, file_path: str, content: str) -> Dict[str, Any]:
        """Edit an existing file"""
        try:
            full_path = self.validate_workspace_path(workspace_id, file_path)
            
            if not full_path.exists():
                return {
                    "operation": "edit",
                    "path": file_path,
                    "success": False,
                    "message": f"File {file_path} does not exist"
                }
            
            async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            return {
                "operation": "edit",
                "path": file_path,
                "success": True,
                "message": f"File {file_path} edited successfully"
            }
        except Exception as e:
            return {
                "operation": "edit",
                "path": file_path,
                "success": False,
                "message": f"Failed to edit file: {str(e)}"
            }
    
    async def append_to_file(self, workspace_id: str, file_path: str, content: str) -> Dict[str, Any]:
        """Append content to an existing file"""
        try:
            full_path = self.validate_workspace_path(workspace_id, file_path)
            
            if not full_path.exists():
                return {
                    "operation": "append",
                    "path": file_path,
                    "success": False,
                    "message": f"File {file_path} does not exist"
                }
            
            async with aiofiles.open(full_path, 'a', encoding='utf-8') as f:
                await f.write(content)
            
            return {
                "operation": "append",
                "path": file_path,
                "success": True,
                "message": f"Content appended to {file_path} successfully"
            }
        except Exception as e:
            return {
                "operation": "append",
                "path": file_path,
                "success": False,
                "message": f"Failed to append to file: {str(e)}"
            }
    
    async def delete_file(self, workspace_id: str, file_path: str) -> Dict[str, Any]:
        """Delete a file or directory"""
        try:
            full_path = self.validate_workspace_path(workspace_id, file_path)
            
            if not full_path.exists():
                return {
                    "operation": "delete",
                    "path": file_path,
                    "success": False,
                    "message": f"File {file_path} does not exist"
                }
            
            if full_path.is_file():
                full_path.unlink()
            else:
                shutil.rmtree(full_path)
            
            return {
                "operation": "delete",
                "path": file_path,
                "success": True,
                "message": f"{'File' if full_path.is_file() else 'Directory'} {file_path} deleted successfully"
            }
        except Exception as e:
            return {
                "operation": "delete",
                "path": file_path,
                "success": False,
                "message": f"Failed to delete {file_path}: {str(e)}"
            }
    
    async def rename_file(self, workspace_id: str, old_path: str, new_path: str) -> Dict[str, Any]:
        """Rename a file or directory"""
        try:
            old_full_path = self.validate_workspace_path(workspace_id, old_path)
            new_full_path = self.validate_workspace_path(workspace_id, new_path)
            
            if not old_full_path.exists():
                return {
                    "operation": "rename",
                    "path": old_path,
                    "new_path": new_path,
                    "success": False,
                    "message": f"File {old_path} does not exist"
                }
            
            if new_full_path.exists():
                return {
                    "operation": "rename",
                    "path": old_path,
                    "new_path": new_path,
                    "success": False,
                    "message": f"Target path {new_path} already exists"
                }
            
            # Ensure parent directory exists
            new_full_path.parent.mkdir(parents=True, exist_ok=True)
            
            old_full_path.rename(new_full_path)
            
            return {
                "operation": "rename",
                "path": old_path,
                "new_path": new_path,
                "success": True,
                "message": f"Renamed {old_path} to {new_path} successfully"
            }
        except Exception as e:
            return {
                "operation": "rename",
                "path": old_path,
                "new_path": new_path,
                "success": False,
                "message": f"Failed to rename {old_path}: {str(e)}"
            }
    
    async def list_files(self, workspace_id: str, directory_path: str = "") -> Dict[str, Any]:
        """List files in a directory"""
        try:
            full_path = self.validate_workspace_path(workspace_id, directory_path)
            
            if not full_path.exists():
                return {
                    "operation": "list",
                    "path": directory_path,
                    "success": False,
                    "message": f"Directory {directory_path} does not exist"
                }
            
            if not full_path.is_dir():
                return {
                    "operation": "list",
                    "path": directory_path,
                    "success": False,
                    "message": f"{directory_path} is not a directory"
                }
            
            files = []
            for item in full_path.iterdir():
                file_info = FileInfo(
                    name=item.name,
                    path=str(item.relative_to(self.get_workspace_path(workspace_id))),
                    is_directory=item.is_dir(),
                    size=item.stat().st_size if item.is_file() else None,
                    modified_at=datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                )
                files.append(file_info.dict())
            
            return {
                "operation": "list",
                "path": directory_path,
                "success": True,
                "message": f"Listed {len(files)} items in {directory_path}",
                "files": files
            }
        except Exception as e:
            return {
                "operation": "list",
                "path": directory_path,
                "success": False,
                "message": f"Failed to list directory: {str(e)}"
            }
    
    async def execute_operations(self, workspace_id: str, operations: List[FileOperation]) -> List[Dict[str, Any]]:
        """Execute multiple file operations"""
        results = []
        
        for operation in operations:
            if operation.operation == FileOperationType.CREATE:
                result = await self.create_file(workspace_id, operation.path, operation.content or "")
            elif operation.operation == FileOperationType.EDIT:
                result = await self.edit_file(workspace_id, operation.path, operation.content or "")
            elif operation.operation == FileOperationType.APPEND:
                result = await self.append_to_file(workspace_id, operation.path, operation.content or "")
            elif operation.operation == FileOperationType.DELETE:
                result = await self.delete_file(workspace_id, operation.path)
            elif operation.operation == FileOperationType.RENAME:
                result = await self.rename_file(workspace_id, operation.path, operation.new_path or "")
            elif operation.operation == FileOperationType.LIST:
                result = await self.list_files(workspace_id, operation.path)
            else:
                result = {
                    "operation": operation.operation.value,
                    "path": operation.path,
                    "success": False,
                    "message": f"Unknown operation: {operation.operation}"
                }
            
            results.append(result)
        
        return results 
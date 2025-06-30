from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/")
def read_root():
    """Root endpoint - server status"""
    return {"message": "MCP Filesystem Server is running"}


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mcp-filesystem-server"} 
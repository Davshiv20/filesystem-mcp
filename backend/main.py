from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.middleware import setup_error_handlers
from src.config import Settings
from src.routes import health_router,workspace_router,operations_router,prompt_router


settings = Settings()

app = FastAPI(
    title=settings.app_name,
    description="A Model Context Protocol server for filesystem operations",
    version=settings.app_version,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup error handlers
setup_error_handlers(app)

# Include routers
app.include_router(health_router)
app.include_router(workspace_router)
app.include_router(operations_router)
app.include_router(prompt_router)
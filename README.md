# Filesystem MCP

AI-powered file operations using natural language prompts.

## Quick Start

### Backend
```bash
cd backend
poetry install
poetry run uvicorn main:app --reload  
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Create `.env` file in the `backend` directory:

```env
# Together AI Configuration
TOGETHER_API_KEY=your_together_ai_api_key_here

# Server Configuration (optional)
HOST=0.0.0.0
PORT=8000
DEBUG=false

# File System Configuration (optional)
WORKSPACES_DIR=workspaces
MAX_FILE_SIZE=104857600
MAX_WORKSPACE_SIZE=1073741824
MAX_FILES_PER_WORKSPACE=1000

# LLM Configuration (optional)
LLM_MODEL=meta-llama/Llama-3.3-70B-Instruct-Turbo-Free
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=512
LLM_TIMEOUT=30
```

## Usage

1. **Create a workspace** via frontend or API
2. **Open AI prompt modal** and describe what you want to do
3. **Examples:**
   - "Create a Python file called hello.py with a function that prints hello world"
   - "Create a .txt file with my name in it"
   - "List all files in the workspace"

## Features

-  **Natural Language Processing** - Use plain English to create, edit, delete files
-  **Isolated Workspaces** - Each workspace is completely separate
-  **AI Confidence Scoring** - See how confident the AI is about your request
-  **Real-time File Operations** - Files are created instantly in your workspace

## Tech Stack

- **Backend**: FastAPI + Python + Together AI (Llama-3.3-70B) + Pydantic
- **Frontend**: React + TypeScript + Vite
- **File Operations**: Async file system with workspace isolation

## API Endpoints

- `POST /workspace/create` - Create new workspace
- `GET /workspace/` - List all workspaces  
- `POST /prompt/process` - Process natural language prompt
- `GET /health` - Health check

Visit `http://localhost:5173` to use the frontend. 
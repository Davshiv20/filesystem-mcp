#!/usr/bin/env python3
"""
Setup script for Ollama LLM integration
"""

import subprocess
import sys
import platform
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        # Use utf-8 encoding for Windows compatibility
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace'  # Replace problematic characters
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def check_ollama_installed():
    """Check if Ollama is already installed"""
    try:
        result = subprocess.run(
            ["ollama", "--version"], 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_ollama():
    """Install Ollama based on the operating system"""
    system = platform.system().lower()
    
    if system == "windows":
        print("Installing Ollama on Windows...")
        print("Please visit https://ollama.ai/download and download the Windows installer")
        print("After installation, restart your terminal and run this script again")
        return False
    
    elif system == "darwin":  # macOS
        return run_command(
            "curl -fsSL https://ollama.ai/install.sh | sh",
            "Installing Ollama on macOS"
        )
    
    elif system == "linux":
        return run_command(
            "curl -fsSL https://ollama.ai/install.sh | sh",
            "Installing Ollama on Linux"
        )
    
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False


def start_ollama():
    """Start the Ollama service"""
    return run_command("ollama serve", "Starting Ollama service")


def pull_mistral_model():
    """Pull the Mistral model"""
    return run_command("ollama pull mistral", "Pulling Mistral model")


def test_ollama():
    """Test if Ollama is working correctly"""
    print("🧪 Testing Ollama...")
    try:
        result = subprocess.run(
            ["ollama", "run", "mistral", "Hello, world!"],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0:
            print("✅ Ollama test successful!")
            return True
        else:
            print(f"❌ Ollama test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Ollama test timed out")
        return False
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False


def create_env_file():
    """Create a .env file with LLM configuration"""
    env_content = """# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
LLM_TIMEOUT=30
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=1000

# Server Configuration
DEBUG=false
APP_NAME="MCP Filesystem Server"
APP_VERSION="1.0.0"

# Workspace Configuration
BASE_WORKSPACE_DIR=workspaces
MAX_WORKSPACE_SIZE_MB=100

# Security Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# File Operation Configuration
MAX_FILE_SIZE_MB=10
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w", encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Created .env file with default configuration")
    else:
        print("ℹ️  .env file already exists")


def main():
    """Main setup function"""
    print("🚀 Setting up Ollama for MCP Filesystem Server")
    print("=" * 50)
    
    # Check if Ollama is already installed
    if check_ollama_installed():
        print("✅ Ollama is already installed")
    else:
        print("📥 Ollama not found, installing...")
        if not install_ollama():
            print("❌ Failed to install Ollama")
            sys.exit(1)
    
    # Start Ollama service
    print("\n🔄 Starting Ollama service...")
    print("Note: This will start Ollama in the background")
    print("You can stop it later with: pkill ollama")
    
    # Start Ollama in background
    try:
        subprocess.Popen(
            ["ollama", "serve"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            encoding='utf-8',
            errors='replace'
        )
        print("✅ Ollama service started")
    except Exception as e:
        print(f"❌ Failed to start Ollama service: {e}")
        sys.exit(1)
    
    # Wait a moment for service to start
    import time
    print("⏳ Waiting for Ollama service to be ready...")
    time.sleep(5)
    
    # Pull Mistral model
    if not pull_mistral_model():
        print("❌ Failed to pull Mistral model")
        sys.exit(1)
    
    # Test Ollama
    if not test_ollama():
        print("❌ Ollama test failed")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Install Python dependencies: poetry install")
    print("2. Start the server: poetry run start")
    print("3. Visit http://localhost:8000/docs to see the API")
    print("\n🔧 Configuration:")
    print("- Edit .env file to customize settings")
    print("- Change OLLAMA_MODEL to use a different model")
    print("- Adjust LLM_TEMPERATURE for different response styles")


if __name__ == "__main__":
    main() 
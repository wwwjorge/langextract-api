#!/usr/bin/env python3
"""Setup script for LangExtract API."""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, check=True, shell=True):
    """Run a command and return the result."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python version: {sys.version}")


def check_docker():
    """Check if Docker is available."""
    try:
        result = run_command("docker --version", check=False)
        if result.returncode == 0:
            print("✓ Docker is available")
            return True
        else:
            print("⚠ Docker is not available")
            return False
    except FileNotFoundError:
        print("⚠ Docker is not installed")
        return False


def check_docker_compose():
    """Check if Docker Compose is available."""
    try:
        result = run_command("docker-compose --version", check=False)
        if result.returncode == 0:
            print("✓ Docker Compose is available")
            return True
        else:
            # Try docker compose (newer syntax)
            result = run_command("docker compose version", check=False)
            if result.returncode == 0:
                print("✓ Docker Compose (v2) is available")
                return True
            else:
                print("⚠ Docker Compose is not available")
                return False
    except FileNotFoundError:
        print("⚠ Docker Compose is not installed")
        return False


def create_env_file():
    """Create .env file from .env.example if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✓ Created .env file from .env.example")
        print("⚠ Please edit .env file with your API keys and configuration")
    elif env_file.exists():
        print("✓ .env file already exists")
    else:
        print("⚠ .env.example not found")


def create_directories():
    """Create necessary directories."""
    directories = ["uploads", "outputs", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")


def install_python_dependencies():
    """Install Python dependencies."""
    print("Installing Python dependencies...")
    
    # Install langextract from source
    run_command("pip install -e .")
    
    # Install API dependencies
    run_command("pip install -r requirements.api.txt")
    
    print("✓ Python dependencies installed")


def setup_docker():
    """Setup Docker environment."""
    if not check_docker() or not check_docker_compose():
        print("Docker setup skipped - Docker not available")
        return False
    
    print("Setting up Docker environment...")
    
    # Build the API image
    run_command("docker-compose build langextract-api")
    
    # Pull Ollama image
    run_command("docker-compose pull ollama")
    
    print("✓ Docker environment setup complete")
    return True


def test_installation():
    """Test the installation."""
    print("Testing installation...")
    
    try:
        # Test langextract import
        import langextract
        print("✓ LangExtract import successful")
        
        # Test API imports
        from api.main import app
        from api.config import get_settings
        print("✓ API imports successful")
        
        # Test settings
        settings = get_settings()
        print(f"✓ Settings loaded - Default model: {settings.default_model_id}")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Test error: {e}")
        return False


def print_usage_instructions():
    """Print usage instructions."""
    print("\n" + "="*60)
    print("🎉 LangExtract API Setup Complete!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Edit .env file with your API keys:")
    print("   - GEMINI_API_KEY=your-gemini-key")
    print("   - OPENAI_API_KEY=your-openai-key")
    print("   - API_SECRET_KEY=your-secret-key")
    
    print("\n🚀 Running the API:")
    print("\n🐳 With Docker (recommended):")
    print("   docker-compose up -d")
    print("   # API will be available at http://localhost:8000")
    print("   # Ollama will be available at http://localhost:11434")
    
    print("\n🐍 With Python directly:")
    print("   python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload")
    
    print("\n📚 API Documentation:")
    print("   http://localhost:8000/docs (Swagger UI)")
    print("   http://localhost:8000/redoc (ReDoc)")
    
    print("\n🔐 Authentication:")
    print("   Default credentials: admin/admin")
    print("   POST /auth/token to get access token")
    
    print("\n🛠 Management Commands:")
    print("   docker-compose logs -f langextract-api  # View API logs")
    print("   docker-compose logs -f ollama           # View Ollama logs")
    print("   docker-compose down                     # Stop services")
    print("   docker-compose up --build               # Rebuild and start")
    
    print("\n📖 Example API Usage:")
    print("   curl -X POST http://localhost:8000/auth/token \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"username\": \"admin\", \"password\": \"admin\"}'")
    
    print("\n⚠️  Important Notes:")
    print("   - Change default passwords in production")
    print("   - Set strong API_SECRET_KEY in .env")
    print("   - Configure CORS settings for your domain")
    print("   - Monitor logs for any issues")
    
    print("\n" + "="*60)


def main():
    """Main setup function."""
    print("🔧 LangExtract API Setup")
    print("=" * 30)
    
    # Check requirements
    check_python_version()
    docker_available = check_docker() and check_docker_compose()
    
    # Setup steps
    create_env_file()
    create_directories()
    
    # Choose installation method
    if docker_available:
        print("\n🐳 Docker is available. Choose installation method:")
        print("1. Docker (recommended)")
        print("2. Python only")
        print("3. Both")
        
        choice = input("Enter choice (1-3) [1]: ").strip() or "1"
        
        if choice in ["1", "3"]:
            setup_docker()
        
        if choice in ["2", "3"]:
            install_python_dependencies()
            test_installation()
    else:
        print("\n🐍 Installing with Python only...")
        install_python_dependencies()
        test_installation()
    
    print_usage_instructions()


if __name__ == "__main__":
    main()
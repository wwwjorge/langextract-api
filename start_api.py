#!/usr/bin/env python3
"""Script to start the LangExtract API server."""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
api_dir = current_dir / "api"
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(api_dir))

if __name__ == "__main__":
    # Load environment variables from both locations
    from dotenv import load_dotenv
    import uvicorn
    
    load_dotenv()  # Load from current directory
    load_dotenv(api_dir / ".env")  # Load from api directory
    
    # Get configuration
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', '8001'))
    
    print(f"🚀 Starting LangExtract API on http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔍 ReDoc Documentation: http://{host}:{port}/redoc")
    print(f"❤️ Health Check: http://{host}:{port}/health")
    
    # Change to API directory and run
    os.chdir(api_dir)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
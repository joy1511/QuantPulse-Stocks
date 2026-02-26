"""
QuantPulse Backend Runner Script

This script provides a convenient way to start the FastAPI server.
Run this file directly: python run.py

The server will start at http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
"""

import uvicorn
from app.config import HOST, PORT

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting QuantPulse India Backend")
    print(f"📍 Server: http://localhost:{PORT}")
    print(f"📚 API Docs: http://localhost:{PORT}/docs")
    print(f"❤️  Health: http://localhost:{PORT}/health")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",      # Path to the FastAPI app
        host=HOST,           # Listen on all interfaces
        port=PORT,           # Port number
        reload=True,         # Auto-reload on code changes (dev mode)
        log_level="info"     # Logging verbosity
    )

"""
Development server runner for Sentopic API

Run this script to start the API server in development mode.
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Sentopic API Development Server...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health") 
    print("🔄 Auto-reload enabled - server will restart when code changes")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 60)
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
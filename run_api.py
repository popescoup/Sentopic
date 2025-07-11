"""
Development server runner for Sentopic API

Run this script to start the API server in development mode.
"""

import uvicorn
import signal
import sys

def signal_handler(sig, frame):
    print("\n🛑 Graceful shutdown initiated...")
    print("⏳ Waiting for background tasks to complete...")
    sys.exit(0)

if __name__ == "__main__":
    print("🚀 Starting Sentopic API Development Server...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health") 
    print("🔄 Auto-reload enabled - server will restart when code changes")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 60)

    # Handle graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
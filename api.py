"""
Sentopic FastAPI Application

API layer that exposes backend functionality through HTTP endpoints.
Provides clean separation between CLI tools and web interface.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, Any

# Initialize FastAPI application with enhanced documentation
app = FastAPI(
    title="Sentopic API",
    description="""
    ## Reddit Analytics Tool API

    Advanced Reddit discussion analysis with AI-powered insights.

    ### Key Features
    * **Project Management**: Create and manage research projects
    * **Analytics Engine**: Comprehensive sentiment and trend analysis  
    * **AI Integration**: LLM-powered insights and chat capabilities
    * **Data Collection**: Reddit data collection and management

    ### API Organization
    * **System**: Health checks and system status
    * **Projects**: Project lifecycle management
    * **Analytics**: Analysis execution and results
    * **Collections**: Reddit data collection management
    * **AI**: Chat agent and LLM features
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "system",
            "description": "System health and status endpoints"
        },
        {
            "name": "projects", 
            "description": "Project management and lifecycle operations"
        },
        {
            "name": "analytics",
            "description": "Analysis execution and results retrieval"
        },
        {
            "name": "collections",
            "description": "Reddit data collection management"
        },
        {
            "name": "ai",
            "description": "AI-powered features including chat and insights"
        }
    ]
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    print("🚀 Sentopic API starting up...")
    print("📚 API Documentation available at: http://localhost:8000/docs")

@app.on_event("shutdown") 
async def shutdown_event():
    """Application shutdown cleanup."""
    print("👋 Sentopic API shutting down...")

@app.get("/health", tags=["system"], summary="System Health Check")
async def health_check() -> Dict[str, Any]:
    """
    **System Health Check**
    
    Returns comprehensive system status including:
    
    * **Service Status**: Overall API health (healthy/degraded/unhealthy)
    * **Component Status**: Individual backend component availability
    * **Timestamp**: Current system time
    * **Version Info**: API version information
    
    **Response Status Levels:**
    * `healthy` - All components operational
    * `degraded` - Some components unavailable but core functionality intact  
    * `unhealthy` - Critical system issues detected
    
    **Use Case:** Frontend applications should call this endpoint to verify
    backend connectivity and display system status to users.
    """
    try:
        # Basic system info
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "Sentopic API",
            "version": "1.0.0"
        }
        
        # Check backend components availability
        components = {}
        
        # Test database connection
        try:
            from src.database import db
            # Simple test - try to get session
            session = db.get_session()
            session.close()
            components["database"] = "available"
        except Exception as e:
            components["database"] = f"unavailable: {str(e)}"
        
        # Test LLM availability
        try:
            from src.llm import is_llm_available
            if is_llm_available():
                components["llm"] = "available"
            else:
                components["llm"] = "configured but not available"
        except Exception as e:
            components["llm"] = f"unavailable: {str(e)}"
        
        # Test analytics engine
        try:
            from src.analytics import analytics_engine
            components["analytics"] = "available"
        except Exception as e:
            components["analytics"] = f"unavailable: {str(e)}"
        
        health_data["components"] = components
        
        # Determine overall health
        if any("unavailable" in status for status in components.values()):
            health_data["status"] = "degraded"
        
        return health_data
        
    except Exception as e:
        # If health check itself fails, return minimal error info
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "Sentopic API",
            "version": "1.0.0",
            "error": f"Health check failed: {str(e)}"
        }
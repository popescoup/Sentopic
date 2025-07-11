from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, Any

# Import your service layer and models
from src.api.services import ProjectService
from src.api.models import ProjectListResponse, ProjectCreate, ProjectResponse, APIError

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

# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================

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

# ============================================================================
# PROJECT ENDPOINTS
# ============================================================================

@app.get("/projects", 
         response_model=ProjectListResponse,
         responses={500: {"model": APIError}},
         tags=["projects"],
         summary="List All Projects",
         description="Get all research projects for the dashboard view")
async def list_projects() -> ProjectListResponse:
    """
    **List All Research Projects**
    
    Returns all user projects with summary information needed for the dashboard.
    Each project includes basic stats, status, and AI summary preview if available.
    
    **Use Case**: Powers the main Projects Dashboard where users can see all
    their research projects and click to open them.
    
    **Response Data**:
    * Project metadata (name, creation date, status)
    * Analysis statistics (mentions, sentiment, keywords count)
    * AI summary previews (first 2-3 sentences)
    * Collection information (subreddits analyzed)
    """
    try:
        projects = await ProjectService.get_all_projects()
        
        return ProjectListResponse(
            projects=projects,
            total_count=len(projects)
        )
        
    except Exception as e:
        # Log error for debugging
        print(f"Error in list_projects endpoint: {e}")
        
        # Return empty list rather than failing - more user-friendly
        return ProjectListResponse(
            projects=[],
            total_count=0
        )

@app.post("/projects",
          response_model=ProjectResponse,
          status_code=201,
          responses={
              400: {"model": APIError, "description": "Validation error"},
              404: {"model": APIError, "description": "Collection not found"},
              500: {"model": APIError, "description": "Server error"}
          },
          tags=["projects"],
          summary="Create New Project",
          description="Create a new research project and analysis session")
async def create_project(project_data: ProjectCreate) -> ProjectResponse:
    """
    **Create New Research Project**
    
    Creates a new research project with the specified parameters. This will:
    
    1. Validate the input data (keywords, collections, etc.)
    2. Create a new analysis session in the backend
    3. Return the project details ready for the frontend
    
    **Use Case**: Called when user completes the "New Project" wizard
    and clicks "Start Analysis"
    
    **Request Body**:
    * **name**: User-defined project name
    * **research_question**: Optional business question driving the research
    * **keywords**: List of keywords to analyze (minimum 1 required)
    * **collection_ids**: List of collection IDs to analyze (minimum 1 required)
    * **partial_matching**: Whether to use partial keyword matching (default: false)
    * **context_window_words**: Words before/after keyword for sentiment (default: 5)
    * **generate_summary**: Whether to generate AI summary after analysis (default: false)
    
    **Response**: Complete project object with generated ID and initial status
    """
    try:
        # Create the project using service layer
        new_project = await ProjectService.create_project(project_data)
        
        return new_project
        
    except ValueError as e:
        # Handle validation errors
        error_message = str(e)
        
        if "Collection(s) not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "collections_not_found",
                    "message": error_message,
                    "details": {"invalid_collection_ids": error_message.split(": ")[1]}
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "validation_error",
                    "message": error_message,
                    "details": {}
                }
            )
    
    except Exception as e:
        # Handle unexpected server errors
        print(f"Unexpected error in create_project endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while creating the project",
                "details": {}
            }
        )

@app.get("/projects/{project_id}",
         response_model=ProjectResponse,
         responses={
             404: {"model": APIError, "description": "Project not found"},
             500: {"model": APIError, "description": "Server error"}
         },
         tags=["projects"],
         summary="Get Project Details",
         description="Get detailed information about a specific project")
async def get_project(project_id: str) -> ProjectResponse:
    """
    **Get Project Details**
    
    Returns complete details for a specific research project including:
    
    * Full project metadata and configuration
    * Analysis results and statistics
    * AI-generated summaries (if available)
    * Collection information and metadata
    
    **Use Case**: Powers the Project Workspace view when user clicks on
    a project from the dashboard.
    
    **Path Parameters**:
    * **project_id**: Unique identifier of the project to retrieve
    
    **Response**: Complete project object with all analysis data and insights
    """
    try:
        project = await ProjectService.get_project_by_id(project_id)
        
        if not project:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "project_not_found",
                    "message": f"Project with ID '{project_id}' not found",
                    "details": {"project_id": project_id}
                }
            )
        
        return project
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        # Handle unexpected server errors
        print(f"Unexpected error in get_project endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while retrieving the project",
                "details": {"project_id": project_id}
            }
        )

@app.delete("/projects/{project_id}",
            status_code=204,
            responses={
                404: {"model": APIError, "description": "Project not found"},
                500: {"model": APIError, "description": "Server error"}
            },
            tags=["projects"],
            summary="Delete Project",
            description="Delete a project and all its associated data")
async def delete_project(project_id: str):
    """
    **Delete Project**
    
    Permanently deletes a research project and all associated data including:
    
    * Analysis session and results
    * Keyword mentions and statistics
    * AI summaries and chat sessions
    * All derived analytics data
    
    **⚠️ Warning**: This operation cannot be undone. The original Reddit
    collections will remain intact, but all analysis specific to this
    project will be permanently removed.
    
    **Use Case**: Called when user confirms deletion from the project
    management interface.
    
    **Path Parameters**:
    * **project_id**: Unique identifier of the project to delete
    
    **Response**: HTTP 204 (No Content) on successful deletion
    """
    try:
        success = await ProjectService.delete_project(project_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "project_not_found",
                    "message": f"Project with ID '{project_id}' not found",
                    "details": {"project_id": project_id}
                }
            )
        
        # Return 204 No Content (FastAPI handles this automatically when no return value)
        return
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except ValueError as e:
        # Handle deletion errors
        print(f"Deletion error in delete_project endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "deletion_failed",
                "message": str(e),
                "details": {"project_id": project_id}
            }
        )
    except Exception as e:
        # Handle unexpected server errors
        print(f"Unexpected error in delete_project endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while deleting the project",
                "details": {"project_id": project_id}
            }
        )
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, Any, Optional, List
from typing import Union

from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# Import your service layer and models
from src.api.services import ProjectService, CollectionService
from src.api.models import (
    ProjectListResponse, ProjectCreate, ProjectResponse, APIError,
    ChatMessageCreate, ChatResponse, ChatSessionListResponse, ChatHistoryResponse,
    KeywordSuggestionRequest, KeywordSuggestionResponse, SubredditSuggestionRequest, SubredditSuggestionResponse, AIStatusResponse,
    CollectionCreateRequest, CollectionBatchResponse, CollectionBatchStatusResponse,
    CollectionListResponse, IndexingRequest, IndexingResponse, IndexingStatusResponse,
    FilteredContextsResponse, TrendsResponse
)

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
    * **Analysis Workflow**: Background processing with real-time status tracking
    * **AI Chat Agent**: Interactive chat with your analysis data
    * **Keyword Suggestions**: AI-powered keyword recommendations
    * **Collection Management**: CRUD operations for Reddit data collections

    ### API Organization
    * **System**: Health checks and system status
    * **Projects**: Project lifecycle management
    * **Analysis**: Analysis execution, progress tracking, and results
    * **Collections**: Reddit data collection management
    * **AI**: Chat agent, keyword suggestions, and LLM features
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
            "name": "analysis",
            "description": "Analysis execution, progress tracking, and results retrieval"
        },
        {
            "name": "collections",
            "description": "Reddit data collection management"
        },
        {
            "name": "ai",
            "description": "AI-powered features including chat, keyword suggestions, and insights"
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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("🚨 Validation Error Details:")
    print(f"📧 Request body: {exc.body}")
    print(f"🔍 Errors: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({
            "error": "validation_error", 
            "message": "Request validation failed",
            "details": exc.errors(),
            "body": exc.body
        })
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

# ============================================================================
# ANALYSIS WORKFLOW ENDPOINTS (STEP 3)
# ============================================================================

@app.post("/projects/{project_id}/analysis/start",
          responses={
              200: {"description": "Analysis started successfully"},
              404: {"model": APIError, "description": "Project not found"},
              409: {"model": APIError, "description": "Analysis already running"},
              500: {"model": APIError, "description": "Server error"}
          },
          tags=["analysis"],
          summary="Start Analysis",
          description="Start analysis processing for a project")
async def start_analysis(project_id: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    **Start Analysis Processing**
    
    Initiates the comprehensive analysis workflow for a research project including:
    
    * **Keyword Analysis**: Finding all keyword mentions in collected data
    * **Sentiment Analysis**: VADER sentiment analysis for each mention
    * **Co-occurrence Analysis**: Identifying keyword relationships
    * **Trend Analysis**: Temporal patterns and changes
    * **AI Summary Generation**: Optional LLM-powered insights (if configured)
    
    **Analysis Process**:
    1. Validates project exists and is ready for analysis
    2. Starts background processing (non-blocking)
    3. Returns immediately with status confirmation
    4. Updates project status as analysis progresses
    
    **Use Case**: Called when user clicks "Start Analysis" in the project setup
    wizard or "Re-run Analysis" in the project workspace.
    
    **Path Parameters**:
    * **project_id**: Unique identifier of the project to analyze
    
    **Response**: Immediate confirmation with status information
    """
    try:
        # Start analysis using service layer
        result = await ProjectService.start_analysis(project_id, background_tasks)
        
        return result
        
    except ValueError as e:
        error_message = str(e)
        
        if "not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "project_not_found",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        elif "already running" in error_message or "already completed" in error_message:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "analysis_conflict",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "analysis_error",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
    
    except Exception as e:
        print(f"Unexpected error in start_analysis endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while starting analysis",
                "details": {"project_id": project_id}
            }
        )

@app.get("/projects/{project_id}/analysis/status",
         responses={
             200: {"description": "Analysis status retrieved successfully"},
             404: {"model": APIError, "description": "Project not found"},
             500: {"model": APIError, "description": "Server error"}
         },
         tags=["analysis"],
         summary="Get Analysis Status",
         description="Get current analysis progress and status for a project")
async def get_analysis_status(project_id: str) -> Dict[str, Any]:
    """
    **Get Analysis Progress and Status**
    
    Returns comprehensive status information for ongoing or completed analysis including:
    
    * **Current Status**: `'running'`, `'completed'`, `'failed'`
    * **Progress Information**: Current phase and completion estimates
    * **Performance Metrics**: Processing speed and estimated time remaining
    * **Error Details**: Detailed error information if analysis failed
    * **Partial Results**: Available data if analysis is in progress
    
    **Status Values**:
    * `running` - Analysis is actively processing
    * `completed` - Analysis finished successfully, results available
    * `failed` - Analysis encountered an error and stopped
    
    **Use Case**: Powers the Analysis Progress Screen with real-time updates.
    Frontend should poll this endpoint every 2-3 seconds during analysis.
    
    **Path Parameters**:
    * **project_id**: Unique identifier of the project to check
    
    **Response**: Detailed status information with progress indicators
    """
    try:
        status = await ProjectService.get_analysis_status(project_id)
        
        return status
        
    except ValueError as e:
        error_message = str(e)
        
        if "not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "project_not_found",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "status_error",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
    
    except Exception as e:
        print(f"Unexpected error in get_analysis_status endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while retrieving analysis status",
                "details": {"project_id": project_id}
            }
        )

@app.get("/projects/{project_id}/analysis/results",
         response_model=ProjectResponse,
         responses={
             200: {"description": "Analysis results retrieved successfully"},
             404: {"model": APIError, "description": "Project not found"},
             409: {"model": APIError, "description": "Analysis not completed"},
             500: {"model": APIError, "description": "Server error"}
         },
         tags=["analysis"],
         summary="Get Analysis Results",
         description="Get complete analysis results for a project")
async def get_analysis_results(project_id: str) -> ProjectResponse:
    """
    **Get Complete Analysis Results**
    
    Returns comprehensive analysis results for a completed project including:
    
    * **Keyword Statistics**: Mention counts, sentiment scores, and distributions
    * **Trend Analysis**: Temporal patterns and changes over time
    * **Co-occurrence Data**: Keyword relationships and associations
    * **Sentiment Insights**: Overall sentiment patterns and keyword-specific sentiment
    * **AI Summary**: LLM-generated insights and business implications (if available)
    * **Representative Examples**: Sample discussions that illustrate key findings
    
    **Result Categories**:
    * **Quantitative Analytics**: Statistical patterns from your keyword analysis
    * **Qualitative Insights**: AI-powered interpretation of discussion patterns
    * **Actionable Intelligence**: Business-relevant insights extracted from Reddit discussions
    
    **Use Case**: Powers the Project Workspace main dashboard with comprehensive
    insights. Only available after analysis status is `'completed'`.
    
    **Path Parameters**:
    * **project_id**: Unique identifier of the project to get results for
    
    **Response**: Complete project object with full analysis results and insights
    """
    try:
        results = await ProjectService.get_analysis_results(project_id)
        
        return results
        
    except ValueError as e:
        error_message = str(e)
        
        if "not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "project_not_found",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        elif "not completed" in error_message:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "analysis_not_completed",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "results_error",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
    
    except Exception as e:
        print(f"Unexpected error in get_analysis_results endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while retrieving analysis results",
                "details": {"project_id": project_id}
            }
        )

@app.post("/projects/{project_id}/indexing",
          response_model=IndexingResponse,
          responses={
              200: {"description": "Indexing started successfully"},
              400: {"model": APIError, "description": "Invalid request or provider not configured"},
              404: {"model": APIError, "description": "Project not found"},
              409: {"model": APIError, "description": "Analysis not completed"},
              500: {"model": APIError, "description": "Server error"}
          },
          tags=["analysis"],
          summary="Start Content Indexing",
          description="Start indexing project content for semantic search capabilities")
async def start_indexing(project_id: str, indexing_request: IndexingRequest, 
                         background_tasks: BackgroundTasks) -> IndexingResponse:
    """
    **Start Content Indexing for Semantic Search**
    
    Initiates background indexing of Reddit content to enable semantic search capabilities including:
    
    * **Local Semantic Search**: Free, privacy-focused search using local sentence-transformers
    * **Cloud Semantic Search**: Advanced search using OpenAI embeddings (requires API key)
    * **Enhanced Chat Experience**: Better AI responses with semantic understanding
    * **Conceptual Queries**: Find discussions by meaning, not just keywords
    
    **Indexing Process**:
    1. Validates project exists and analysis is completed
    2. Generates vector embeddings for all posts and comments
    3. Stores embeddings for fast similarity search
    4. Enables semantic search in chat and direct queries
    
    **Provider Options**:
    * **local**: Free offline embeddings using sentence-transformers (recommended for privacy)
    * **openai**: Advanced cloud embeddings using OpenAI API (requires API key and costs tokens)
    
    **Use Case**: Called when user wants to enable semantic search capabilities
    for more sophisticated AI chat interactions and conceptual content discovery.
    
    **Path Parameters**:
    * **project_id**: Unique identifier of the project to index
    
    **Request Body**:
    * **provider_type**: Either "local" (free) or "openai" (paid API)
    * **force_reindex**: Whether to reindex if already indexed (default: false)
    
    **Response**: Immediate confirmation with estimated completion time
    """
    try:
        # Start indexing using service layer
        result = await ProjectService.start_indexing(project_id, indexing_request, background_tasks)
        
        return result
        
    except ValueError as e:
        error_message = str(e)
        
        if "not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "project_not_found",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        elif "not completed" in error_message:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "analysis_not_completed",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        elif "not enabled" in error_message or "not configured" in error_message:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "provider_not_available",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "indexing_error",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
    
    except Exception as e:
        print(f"Unexpected error in start_indexing endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while starting indexing",
                "details": {"project_id": project_id}
            }
        )

@app.get("/projects/{project_id}/indexing/status",
         response_model=IndexingStatusResponse,
         responses={
             200: {"description": "Indexing status retrieved successfully"},
             404: {"model": APIError, "description": "Project not found"},
             500: {"model": APIError, "description": "Server error"}
         },
         tags=["analysis"],
         summary="Get Indexing Status",
         description="Get current indexing status and available search capabilities")
async def get_indexing_status(project_id: str) -> IndexingStatusResponse:
    """
    **Get Indexing Status and Search Capabilities**
    
    Returns comprehensive information about content indexing status and available search capabilities:
    
    * **Indexing Status**: Current state of local and cloud embeddings
    * **Search Capabilities**: Which search types are available for the AI chat
    * **Content Metrics**: How much content is indexed vs. total available
    * **Indexing Progress**: Real-time status if indexing is currently running
    
    **Indexing States**:
    * `none` - No indexing has been performed
    * `partial` - Some content is indexed (interrupted or partial completion)
    * `complete` - All content is fully indexed and ready for semantic search
    
    **Search Capabilities Returned**:
    * **keyword**: Always available - traditional keyword-based search
    * **local_semantic**: Available if local embeddings are indexed
    * **cloud_semantic**: Available if OpenAI embeddings are indexed
    * **analytics_driven**: Available if project analysis is completed
    
    **Use Case**: 
    * Frontend checks capabilities before showing search options in chat UI
    * Determines whether to show "Enable Semantic Search" prompts
    * Monitors indexing progress during background processing
    * Helps users understand what search features are available
    
    **Path Parameters**:
    * **project_id**: Unique identifier of the project to check
    
    **Response**: Complete indexing status with search capability matrix
    """
    try:
        status = await ProjectService.get_indexing_status(project_id)
        
        return status
        
    except ValueError as e:
        error_message = str(e)
        
        if "not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "project_not_found",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "status_error",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
    
    except Exception as e:
        print(f"Unexpected error in get_indexing_status endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while retrieving indexing status",
                "details": {"project_id": project_id}
            }
        )
    
@app.get("/projects/{project_id}/contexts/filtered",
         response_model=FilteredContextsResponse,
         responses={
             200: {"description": "Filtered contexts retrieved successfully"},
             404: {"model": APIError, "description": "Project not found"},
             400: {"model": APIError, "description": "Invalid filter parameters"},
             500: {"model": APIError, "description": "Server error"}
         },
         tags=["analysis"],
         summary="Get Filtered Contexts",
         description="Get filtered and paginated context instances for a project")
async def get_filtered_contexts(
    project_id: str,
    primary_keyword: Optional[str] = Query(None, description="Primary keyword to filter by (optional - if not provided, shows all keywords)"),
    secondary_keyword: Optional[str] = Query(None, description="Secondary keyword for co-occurrence filtering"),
    min_sentiment: float = Query(-1.0, description="Minimum sentiment score", ge=-1.0, le=1.0),
    max_sentiment: float = Query(1.0, description="Maximum sentiment score", ge=-1.0, le=1.0),
    sort_by: str = Query("newest", description="Sort order: newest, oldest, sentiment_asc, sentiment_desc"),
    page: int = Query(1, description="Page number", ge=1),
    limit: int = Query(20, description="Items per page", ge=1, le=100)
) -> FilteredContextsResponse:
    """
    **Get Filtered Context Instances**
    
    Retrieve filtered and paginated context instances where keywords appear in your project data.
    Supports filtering by primary keyword, co-occurrence with secondary keywords, sentiment ranges,
    and multiple sorting options.
    
    **Filtering Options**:
    * **Primary Keyword**: Required - filter contexts containing this keyword
    * **Secondary Keyword**: Optional - only show contexts where both keywords appear in the same post/comment
    * **Sentiment Range**: Filter by sentiment score range (-1.0 to +1.0)
    * **Sorting**: newest (default), oldest, sentiment_asc, sentiment_desc
    
    **Pagination**: Standard page/limit pagination with metadata about total results
    
    **Use Case**: Powers the Context Explorer modal with advanced filtering and navigation capabilities.
    Allows users to drill down into specific keyword mentions and explore actual Reddit discussions
    that contain their keywords of interest.
    
    **Path Parameters**:
    * **project_id**: Unique identifier of the project
    
    **Query Parameters**:
    * **primary_keyword**: Main keyword to search for (required)
    * **secondary_keyword**: Additional keyword for co-occurrence filtering (optional)
    * **min_sentiment/max_sentiment**: Sentiment score range filtering
    * **sort_by**: Sorting method (newest/oldest/sentiment_asc/sentiment_desc)
    * **page**: Page number for pagination (starts at 1)
    * **limit**: Number of results per page (1-100, default 20)
    
    **Response**: Filtered contexts with full content, pagination info, and applied filters
    """
    try:
        # Create filters object
        filters = {
            'primary_keyword': primary_keyword,
            'secondary_keyword': secondary_keyword,
            'min_sentiment': min_sentiment,
            'max_sentiment': max_sentiment,
            'sort_by': sort_by,
            'page': page,
            'limit': limit
        }
        
        # Get filtered contexts using service layer
        result = await ProjectService.get_filtered_contexts(project_id, filters)
        
        return result
        
    except ValueError as e:
        error_message = str(e)
        
        if "not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "project_not_found",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "filter_error",
                    "message": error_message,
                    "details": {"project_id": project_id, "filters": filters}
                }
            )
    
    except Exception as e:
        print(f"Unexpected error in get_filtered_contexts endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while retrieving filtered contexts",
                "details": {"project_id": project_id}
            }
        )
    
@app.get("/projects/{project_id}/trends",
         response_model=TrendsResponse,
         responses={
             200: {"description": "Trends analysis retrieved successfully"},
             400: {"model": APIError, "description": "Invalid parameters or keywords not in project"},
             404: {"model": APIError, "description": "Project not found"},
             409: {"model": APIError, "description": "Analysis not completed"},
             500: {"model": APIError, "description": "Server error"}
         },
         tags=["analysis"],
         summary="Get Trends Analysis",
         description="Get trends analysis for specific keywords with chart-optimized data")
async def get_project_trends(
    project_id: str,
    keywords: List[str] = Query(..., description="Keywords to analyze (max 5)"),
    time_period: str = Query("weekly", description="Time period: daily, weekly, monthly")
) -> TrendsResponse:
    """
    **Get Trends Analysis for Keywords**
    
    Returns trend analysis data optimized for chart visualization with mention frequency 
    and sentiment trends over time for specified keywords.
    
    **Features**:
    * **Multi-keyword comparison**: Analyze up to 5 keywords simultaneously
    * **Flexible time periods**: Daily, weekly, or monthly granularity
    * **Chart-ready format**: Data structure optimized for Recharts visualization
    * **Complete time series**: Fills gaps with zero values for continuous charts
    * **Dual trend types**: Same data supports both mention frequency and sentiment charts
    
    **Chart Integration**:
    * Data format designed for Recharts LineChart components
    * Dynamic field names for each keyword (e.g., 'battery_mentions', 'battery_sentiment')
    * Human-readable date labels for chart axes
    * Consistent time series without gaps
    
    **Use Case**: Powers the Trends Analysis Modal in the Project Workspace, allowing users
    to visualize how keyword mentions and sentiment change over time with interactive controls.
    
    **Path Parameters**:
    * **project_id**: Unique identifier of the project to analyze
    
    **Query Parameters**:
    * **keywords**: Array of keywords to include in analysis (must exist in project, max 5)
    * **time_period**: Granularity for time grouping ('daily', 'weekly', 'monthly')
    
    **Response**: Chart-optimized trends data with flat structure and complete time series
    
    **Example Usage**:
    ```
    GET /projects/abc123/trends?keywords=battery,charging&time_period=weekly
    ```
    
    **Data Structure**: Each data point contains:
    * `time_period`: ISO date string for the period
    * `formatted_date`: Human-readable label for charts
    * `{keyword}_mentions`: Mention count for each keyword
    * `{keyword}_sentiment`: Average sentiment for each keyword
    """
    try:
        # Validate time period
        valid_periods = ["daily", "weekly", "monthly"]
        if time_period not in valid_periods:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_time_period",
                    "message": f"Time period must be one of: {valid_periods}",
                    "details": {"provided": time_period, "valid_options": valid_periods}
                }
            )
        
        # Validate keywords list
        if not keywords:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "keywords_required",
                    "message": "At least one keyword is required",
                    "details": {}
                }
            )
        
        if len(keywords) > 5:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "too_many_keywords",
                    "message": "Maximum 5 keywords allowed for performance",
                    "details": {"provided": len(keywords), "maximum": 5}
                }
            )
        
        # Clean keywords (remove duplicates and empty strings)
        clean_keywords = list(set(kw.strip() for kw in keywords if kw.strip()))
        if not clean_keywords:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_keywords",
                    "message": "No valid keywords provided",
                    "details": {}
                }
            )
        
        # Get trends analysis using service layer
        result = await ProjectService.get_project_trends(project_id, clean_keywords, time_period)
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        error_message = str(e)
        
        if "not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "project_not_found",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        elif "not completed" in error_message:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "analysis_not_completed",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        elif "Keywords not found" in error_message:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "keywords_not_in_project",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "trends_error",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
    
    except Exception as e:
        print(f"Unexpected error in get_project_trends endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while retrieving trends analysis",
                "details": {"project_id": project_id}
            }
        )

# ============================================================================
# COLLECTION MANAGEMENT ENDPOINTS (NEW - STEP 5)
# ============================================================================

@app.post("/collections",
          response_model=CollectionBatchResponse,
          status_code=201,
          responses={
              400: {"model": APIError, "description": "Validation error"},
              500: {"model": APIError, "description": "Server error"}
          },
          tags=["collections"],
          summary="Create Collections",
          description="Create Reddit data collections for one or more subreddits")
async def create_collections(request: CollectionCreateRequest, background_tasks: BackgroundTasks) -> CollectionBatchResponse:
    """
    **Create Reddit Data Collections**
    
    Creates Reddit data collections for one or more subreddits using unified parameters.
    This endpoint handles both single subreddit and multi-subreddit collection requests.
    
    **Collection Process**:
    1. Validates subreddit names and collection parameters
    2. Creates individual collection records for each subreddit
    3. Starts background data collection (non-blocking)
    4. Returns batch tracking information for progress monitoring
    
    **What Gets Collected**:
    * Reddit posts based on specified sort method and count
    * Root comments for each post (configurable limit)
    * Replies to root comments (configurable depth)
    * Comment filtering by minimum upvotes
    
    **Use Case**: Called from Collection Manager when user wants to gather
    Reddit data for analysis. Collections can then be used in research projects.
    
    **Request Body**:
    * **subreddits**: Array of subreddit names (1-10 subreddits, without r/ prefix)
    * **collection_params**: Unified parameters applied to all subreddits:
      * **sort_method**: hot, new, rising, top, controversial
      * **time_period**: Required for top/controversial (hour, day, week, month, year, all)
      * **posts_count**: Number of posts to collect per subreddit (1-1000)
      * **root_comments**: Max root comments per post (0-100)
      * **replies_per_root**: Max replies per root comment (0-50)
      * **min_upvotes**: Minimum upvotes for comment inclusion (0+)
    
    **Response**: Batch tracking information with individual collection IDs
    """
    try:
        # Create collections using service layer
        batch_response = await CollectionService.create_collections(request, background_tasks)
        
        return batch_response
        
    except ValueError as e:
        # Handle validation errors
        error_message = str(e)
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
        print(f"Unexpected error in create_collections endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while creating collections",
                "details": {}
            }
        )

@app.get("/collections/{batch_id}/status",
         response_model=CollectionBatchStatusResponse,
         responses={
             200: {"description": "Collection status retrieved successfully"},
             404: {"model": APIError, "description": "Batch not found"},
             500: {"model": APIError, "description": "Server error"}
         },
         tags=["collections"],
         summary="Get Collection Progress",
         description="Get current progress for a collection batch")
async def get_collection_status(batch_id: str) -> CollectionBatchStatusResponse:
    """
    **Get Collection Batch Progress**
    
    Returns comprehensive status information for ongoing or completed collection batches.
    
    **Status Information**:
    * **Overall Progress**: Percentage completion across all subreddits
    * **Current Activity**: Which subreddit is currently being processed
    * **Individual Status**: Status of each collection in the batch
    * **Completion Stats**: Lists of completed and failed subreddits
    * **Time Estimates**: Estimated completion time based on current progress
    
    **Use Case**: Powers the Collection Progress Screen with real-time updates.
    Frontend should poll this endpoint every 2-3 seconds during active collection.
    
    **Path Parameters**:
    * **batch_id**: Unique batch identifier returned from collection creation
    
    **Response**: Detailed progress information with individual collection statuses
    """
    try:
        status = await CollectionService.get_batch_status(batch_id)
        
        return status
        
    except ValueError as e:
        error_message = str(e)
        
        if "not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "batch_not_found",
                    "message": error_message,
                    "details": {"batch_id": batch_id}
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "status_error",
                    "message": error_message,
                    "details": {"batch_id": batch_id}
                }
            )
    
    except Exception as e:
        print(f"Unexpected error in get_collection_status endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while retrieving collection status",
                "details": {"batch_id": batch_id}
            }
        )

@app.get("/collections",
         response_model=CollectionListResponse,
         responses={500: {"model": APIError}},
         tags=["collections"],
         summary="List All Collections",
         description="Get all Reddit data collections")
async def list_collections() -> CollectionListResponse:
    """
    **List All Reddit Data Collections**
    
    Returns all available Reddit data collections that can be used for analysis projects.
    
    **Collection Information**:
    * **Basic Metadata**: Subreddit, creation date, collection parameters
    * **Collection Stats**: Posts collected, comments collected, status
    * **Usage Info**: Which projects are using each collection
    
    **Use Case**: Powers the Collection Manager interface and collection selection
    during project creation. Shows users what data is available for analysis.
    
    **Response**: Complete list of collections with metadata and statistics
    """
    try:
        collections = await CollectionService.get_all_collections()
        
        return collections
        
    except Exception as e:
        # Log error for debugging
        print(f"Error in list_collections endpoint: {e}")
        
        # Return empty list rather than failing - more user-friendly
        return CollectionListResponse(
            collections=[],
            total_count=0
        )

@app.delete("/collections/{collection_id}",
            responses={
                200: {"description": "Multiple collections deleted"},
                204: {"description": "Single collection deleted"},
                400: {"model": APIError, "description": "Validation error"},
                404: {"model": APIError, "description": "Collection(s) not found"},
                500: {"model": APIError, "description": "Server error"}
            },
            tags=["collections"],
            summary="Delete Collection(s)",
            description="Delete one or multiple Reddit data collections")
async def delete_collection(
    collection_id: str, 
    additional_ids: Optional[str] = Query(None, description="Comma-separated additional collection IDs to delete")
) -> Union[None, Dict[str, Any]]:
    """
    **Delete Reddit Data Collection(s)**
    
    Supports both single and multiple collection deletion in one endpoint:
    
    **Single Collection Deletion:**
    ```
    DELETE /collections/collection-abc123
    ```
    
    **Multiple Collection Deletion:**
    ```
    DELETE /collections/collection-abc123?additional_ids=collection-def456,collection-ghi789
    ```
    
    **How It Works:**
    * If only `collection_id` is provided → deletes single collection (HTTP 204)
    * If `additional_ids` query parameter is provided → deletes multiple collections (HTTP 200 with results)
    * For multiple deletions, continues processing even if some fail
    * Returns detailed results showing which succeeded and failed
    
    **⚠️ Warning**: This operation cannot be undone. If any collections are being
    used by research projects, those projects will need to be updated or deleted.
    
    **Path Parameters:**
    * **collection_id**: Primary collection ID to delete
    
    **Query Parameters:**
    * **additional_ids**: Comma-separated list of additional collection IDs (optional)
    
    **Response:**
    * Single deletion: HTTP 204 (No Content)
    * Multiple deletion: HTTP 200 with detailed results
    """
    try:
        # Determine if this is single or multiple deletion
        if additional_ids is None:
            # Single collection deletion (existing behavior)
            success = await CollectionService.delete_collection(collection_id)
            
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "collection_not_found",
                        "message": f"Collection with ID '{collection_id}' not found",
                        "details": {"collection_id": collection_id}
                    }
                )
            
            # Return 204 No Content for single deletion (existing behavior)
            return
        
        else:
            # Multiple collection deletion
            # Parse additional IDs and combine with primary ID
            additional_id_list = [id.strip() for id in additional_ids.split(',') if id.strip()]
            all_collection_ids = [collection_id] + additional_id_list
            
            # Remove duplicates while preserving order
            seen = set()
            unique_ids = []
            for id in all_collection_ids:
                if id not in seen:
                    seen.add(id)
                    unique_ids.append(id)
            
            if len(unique_ids) == 1:
                # Only one unique ID, treat as single deletion
                success = await CollectionService.delete_collection(unique_ids[0])
                
                if not success:
                    raise HTTPException(
                        status_code=404,
                        detail={
                            "error": "collection_not_found",
                            "message": f"Collection with ID '{unique_ids[0]}' not found",
                            "details": {"collection_id": unique_ids[0]}
                        }
                    )
                
                return
            
            # Process multiple deletions
            results = []
            successful_deletions = 0
            failed_deletions = 0
            
            for cid in unique_ids:
                try:
                    success = await CollectionService.delete_collection(cid)
                    
                    if success:
                        results.append({
                            "collection_id": cid,
                            "success": True,
                            "error_message": None
                        })
                        successful_deletions += 1
                    else:
                        results.append({
                            "collection_id": cid,
                            "success": False,
                            "error_message": "Collection not found"
                        })
                        failed_deletions += 1
                        
                except Exception as e:
                    results.append({
                        "collection_id": cid,
                        "success": False,
                        "error_message": str(e)
                    })
                    failed_deletions += 1
            
            # Return detailed results for multiple deletions
            return {
                "total_requested": len(unique_ids),
                "successful_deletions": successful_deletions,
                "failed_deletions": failed_deletions,
                "results": results,
                "message": f"Processed {len(unique_ids)} collections: {successful_deletions} succeeded, {failed_deletions} failed"
            }
            
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except ValueError as e:
        # Handle deletion errors
        print(f"Deletion error in delete_collection endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "deletion_failed",
                "message": str(e),
                "details": {"collection_id": collection_id}
            }
        )
    except Exception as e:
        # Handle unexpected server errors
        print(f"Unexpected error in delete_collection endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while deleting collection(s)",
                "details": {"collection_id": collection_id}
            }
        )
    
# ============================================================================
# CONFIGURATION ENDPOINTS (NEW - PHASE 7.1)
# ============================================================================

@app.get("/config/status",
         responses={200: {"description": "Configuration status retrieved"}},
         tags=["system"],
         summary="Get Configuration Status",
         description="Get current API configuration status and connection tests")
async def get_config_status() -> Dict[str, Any]:
    """
    **Get Configuration Status**
    
    Returns current configuration status for all APIs including:
    * Reddit API connection status and credentials validation
    * LLM providers configuration and connection tests
    * Feature availability based on current configuration
    * Detailed error messages for troubleshooting
    
    **Use Case**: Powers the Settings interface to show current configuration
    status and help users troubleshoot connection issues.
    """
    try:
        from src.config import config
        return config.get_configuration_status()
        
    except Exception as e:
        print(f"Error in get_config_status: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.post("/config/reddit",
          responses={
              200: {"description": "Reddit configuration updated successfully"},
              400: {"model": APIError, "description": "Invalid configuration"},
              500: {"model": APIError, "description": "Server error"}
          },
          tags=["system"],
          summary="Update Reddit Configuration",
          description="Update Reddit API configuration and test connection")
async def update_reddit_config(config_data: Dict[str, str]) -> Dict[str, Any]:
    """
    **Update Reddit API Configuration**
    
    Updates Reddit API credentials and tests the connection.
    
    **Request Body**:
    * **client_id**: Reddit API client ID
    * **client_secret**: Reddit API client secret  
    * **user_agent**: Reddit API user agent string
    
    **Response**: Configuration update result with connection test
    """
    try:
        from src.config import config
        
        # Update configuration
        success, errors = config.update_reddit_config(config_data)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "validation_error",
                    "message": "Invalid Reddit configuration",
                    "details": {"validation_errors": errors}
                }
            )
        
        # Test the connection
        connected, connection_message = config.test_reddit_connection()
        
        return {
            "success": True,
            "message": "Reddit configuration updated successfully",
            "connection_test": {
                "connected": connected,
                "message": connection_message
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_reddit_config: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error", 
                "message": "Failed to update Reddit configuration",
                "details": {"error": str(e)}
            }
        )

@app.post("/config/llm",
          responses={
              200: {"description": "LLM configuration updated successfully"},
              400: {"model": APIError, "description": "Invalid configuration"},
              500: {"model": APIError, "description": "Server error"}
          },
          tags=["system"],
          summary="Update LLM Configuration",
          description="Update LLM provider configuration and test connections")
async def update_llm_config(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    **Update LLM Configuration**
    
    Updates LLM provider configuration and tests connections.
    
    **Request Body**: Complete LLM configuration object
    
    **Response**: Configuration update result with provider connection tests
    """
    try:
        from src.config import config
        
        # Update configuration  
        success, errors = config.update_llm_config(config_data)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "validation_error",
                    "message": "Invalid LLM configuration",
                    "details": {"validation_errors": errors}
                }
            )
        
        # Test provider connections
        provider_tests = config.test_llm_providers()
        
        return {
            "success": True,
            "message": "LLM configuration updated successfully",
            "provider_tests": provider_tests,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_llm_config: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "Failed to update LLM configuration", 
                "details": {"error": str(e)}
            }
        )

@app.post("/config/test-connections",
          responses={
              200: {"description": "Connection tests completed"},
              500: {"model": APIError, "description": "Server error"}
          },
          tags=["system"],
          summary="Test All API Connections",
          description="Test connections to all configured APIs")
async def test_all_connections() -> Dict[str, Any]:
    """
    **Test All API Connections**
    
    Tests connections to Reddit API and all configured LLM providers.
    
    **Response**: Test results for all configured APIs
    """
    try:
        from src.config import config
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "reddit": {"connected": False, "message": "Not tested"},
            "llm_providers": {}
        }
        
        # Test Reddit connection
        try:
            reddit_connected, reddit_message = config.test_reddit_connection()
            results["reddit"] = {
                "connected": reddit_connected,
                "message": reddit_message
            }
        except Exception as e:
            results["reddit"] = {
                "connected": False,
                "message": f"Test failed: {str(e)}"
            }
        
        # Test LLM providers
        try:
            provider_tests = config.test_llm_providers()
            for provider_name, (success, message) in provider_tests.items():
                results["llm_providers"][provider_name] = {
                    "connected": success,
                    "message": message
                }
        except Exception as e:
            results["llm_providers"]["error"] = {
                "connected": False,
                "message": f"LLM tests failed: {str(e)}"
            }
        
        return results
        
    except Exception as e:
        print(f"Error in test_all_connections: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "Failed to test connections",
                "details": {"error": str(e)}
            }
        )

@app.delete("/config/reset",
           responses={
               200: {"description": "Configuration reset successfully"},
               500: {"model": APIError, "description": "Server error"}
           },
           tags=["system"],
           summary="Reset Configuration",
           description="Reset configuration to defaults")
async def reset_configuration() -> Dict[str, Any]:
    """
    **Reset Configuration to Defaults**
    
    Resets all configuration to default values from config.example.json.
    Creates a backup of current configuration before resetting.
    
    **⚠️ Warning**: This will reset all API keys and settings to defaults.
    
    **Response**: Reset operation result with backup information
    """
    try:
        from src.config import config
        
        success, message = config.reset_configuration()
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "reset_failed",
                    "message": message,
                    "details": {}
                }
            )
        
        return {
            "success": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in reset_configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "Failed to reset configuration",
                "details": {"error": str(e)}
            }
        )

@app.delete("/config/clear-data",
           responses={
               200: {"description": "Data cleared successfully"},
               500: {"model": APIError, "description": "Server error"}
           },
           tags=["system"],
           summary="Clear All Data",
           description="Clear all application data (projects, collections, chat history)")
async def clear_all_data() -> Dict[str, Any]:
    """
    **Clear All Application Data**
    
    Permanently deletes all:
    * Research projects and analysis sessions
    * Reddit data collections (posts and comments)
    * Chat sessions and message history
    * AI summaries and embeddings
    
    **⚠️ Warning**: This operation cannot be undone.
    
    **Response**: Data clearing operation result
    """
    try:
        from src.config import config
        
        success, message = config.clear_all_data()
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "clear_failed",
                    "message": message,
                    "details": {}
                }
            )
        
        return {
            "success": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in clear_all_data: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "Failed to clear data",
                "details": {"error": str(e)}
            }
        )

# ============================================================================
# CHAT AND AI ENDPOINTS (EXISTING - STEP 4)
# ============================================================================

@app.get("/projects/{project_id}/chat/sessions",
         response_model=ChatSessionListResponse,
         responses={
             404: {"model": APIError, "description": "Project not found"},
             500: {"model": APIError, "description": "Server error"}
         },
         tags=["ai"],
         summary="List Chat Sessions",
         description="Get all chat sessions for a project")
async def get_chat_sessions(project_id: str) -> ChatSessionListResponse:
    """
    **List Chat Sessions for a Project**
    
    Returns all chat sessions created for a specific project, allowing users to:
    
    * Resume previous conversations with the AI
    * See conversation previews and activity
    * Manage multiple chat threads about the same data
    
    **Use Case**: Powers the chat session selection interface, allowing users
    to continue previous conversations or start new ones.
    
    **Path Parameters**:
    * **project_id**: Project ID to get chat sessions for
    
    **Response**: List of chat sessions with metadata and previews
    """
    try:
        sessions = await ProjectService.get_chat_sessions(project_id)
        return sessions
        
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "project_not_found",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "chat_error",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
    
    except Exception as e:
        print(f"Unexpected error in get_chat_sessions endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while retrieving chat sessions",
                "details": {"project_id": project_id}
            }
        )

@app.post("/projects/{project_id}/chat/sessions",
          status_code=201,
          responses={
              201: {"description": "Chat session created successfully"},
              404: {"model": APIError, "description": "Project not found"},
              400: {"model": APIError, "description": "Project not ready for chat"},
              500: {"model": APIError, "description": "Server error"}
          },
          tags=["ai"],
          summary="Start New Chat Session",
          description="Create a new AI chat session for a project")
async def start_chat_session(project_id: str) -> Dict[str, Any]:
    """
    **Start New AI Chat Session**
    
    Creates a new chat session for interactive AI conversations about your analysis data.
    
    **Requirements**:
    * Project must exist and analysis must be completed
    * AI/LLM features must be available and configured
    
    **What You Get**:
    * Interactive AI that understands your specific analysis results
    * Ability to ask questions about patterns, sentiment, and trends
    * AI can search and reference actual Reddit discussions
    * Contextual explanations of your analytics findings
    
    **Use Case**: Called when user wants to start a new conversation thread
    about their analysis results.
    
    **Path Parameters**:
    * **project_id**: Project ID to create chat session for
    
    **Response**: New chat session information with unique session ID
    """
    try:
        session_info = await ProjectService.start_chat_session(project_id)
        
        return {
            "status": "created",
            "session_id": session_info.session_id,
            "created_at": session_info.created_at.isoformat(),
            "message": "Chat session created successfully. You can now ask questions about your analysis data."
        }
        
    except ValueError as e:
        error_message = str(e)
        
        if "not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "project_not_found",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        elif "not completed" in error_message:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "analysis_not_completed",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        elif "not available" in error_message:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "ai_not_available",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "chat_error",
                    "message": error_message,
                    "details": {"project_id": project_id}
                }
            )
    
    except Exception as e:
        print(f"Unexpected error in start_chat_session endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while starting chat session",
                "details": {"project_id": project_id}
            }
        )

@app.post("/chat/{chat_session_id}/messages",
          response_model=ChatResponse,
          responses={
              404: {"model": APIError, "description": "Chat session not found"},
              400: {"model": APIError, "description": "Invalid message or AI unavailable"},
              500: {"model": APIError, "description": "Server error"}
          },
          tags=["ai"],
          summary="Send Chat Message",
          description="Send a message to the AI chat agent")
async def send_chat_message(chat_session_id: str, message_data: ChatMessageCreate) -> ChatResponse:
    """
    **Send Message to AI Chat Agent**
    
    Send a question or message to the AI agent for intelligent analysis of your data.
    
    **AI Capabilities**:
    * Understands your specific analysis results and can answer questions about patterns
    * Can search through actual Reddit discussions to find relevant examples
    * Explains sentiment trends, keyword relationships, and temporal patterns
    * Provides business insights and actionable recommendations
    * References specific discussions and quotes from your data
    
    **Search Types**:
    * `auto` - AI automatically selects the best search method
    * `keyword` - Traditional keyword-based search
    * `local_semantic` - Local semantic search (requires indexing)
    * `cloud_semantic` - Cloud semantic search (requires indexing)
    * `analytics_driven` - Uses your keyword analysis data for precise results
    
    **Use Case**: Powers the interactive chat interface where users can ask
    natural language questions about their Reddit analysis data.
    
    **Path Parameters**:
    * **chat_session_id**: Unique chat session identifier
    
    **Request Body**:
    * **message**: Your question or message to the AI
    * **search_type**: Search method preference (default: "auto")
    
    **Response**: AI response with source attributions and analytics insights
    """
    try:
        response = await ProjectService.send_chat_message(chat_session_id, message_data)
        return response
        
    except ValueError as e:
        error_message = str(e)
        
        if "not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "chat_session_not_found",
                    "message": error_message,
                    "details": {"chat_session_id": chat_session_id}
                }
            )
        elif "not available" in error_message:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "ai_not_available",
                    "message": error_message,
                    "details": {"chat_session_id": chat_session_id}
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "chat_error",
                    "message": error_message,
                    "details": {"chat_session_id": chat_session_id}
                }
            )
    
    except Exception as e:
        print(f"Unexpected error in send_chat_message endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while processing chat message",
                "details": {"chat_session_id": chat_session_id}
            }
        )

@app.get("/chat/{chat_session_id}/history",
         response_model=ChatHistoryResponse,
         responses={
             404: {"model": APIError, "description": "Chat session not found"},
             500: {"model": APIError, "description": "Server error"}
         },
         tags=["ai"],
         summary="Get Chat History",
         description="Get conversation history for a chat session")
async def get_chat_history(chat_session_id: str, limit: int = 50) -> ChatHistoryResponse:
    """
    **Get Chat Conversation History**
    
    Retrieves the full conversation history for a chat session, including:
    
    * All user messages and AI responses in chronological order
    * Message metadata (timestamps, token usage, costs)
    * Conversation context for resuming discussions
    
    **Use Case**: Powers the chat interface message history and allows users
    to see previous conversations when resuming a chat session.
    
    **Path Parameters**:
    * **chat_session_id**: Unique chat session identifier
    
    **Query Parameters**:
    * **limit**: Maximum number of messages to return (default: 50)
    
    **Response**: Complete conversation history with message details
    """
    try:
        history = await ProjectService.get_chat_history(chat_session_id, limit)
        return history
        
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "chat_session_not_found",
                    "message": error_message,
                    "details": {"chat_session_id": chat_session_id}
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "chat_error",
                    "message": error_message,
                    "details": {"chat_session_id": chat_session_id}
                }
            )
    
    except Exception as e:
        print(f"Unexpected error in get_chat_history endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while retrieving chat history",
                "details": {"chat_session_id": chat_session_id}
            }
        )

@app.post("/ai/keywords/suggest",
          response_model=KeywordSuggestionResponse,
          responses={
              400: {"model": APIError, "description": "Invalid request or AI unavailable"},
              500: {"model": APIError, "description": "Server error"}
          },
          tags=["ai"],
          summary="Get AI Keyword Suggestions",
          description="Get AI-powered keyword suggestions for research topics")
async def suggest_keywords(suggestion_request: KeywordSuggestionRequest) -> KeywordSuggestionResponse:
    """
    **AI-Powered Keyword Suggestions**
    
    Get intelligent keyword suggestions from AI based on your research description.
    
    **How It Works**:
    * Describe what you want to research in natural language
    * AI analyzes your description and suggests relevant keywords
    * Suggestions are optimized for Reddit discussion analysis
    * Keywords focus on how people actually discuss topics on Reddit
    
    **Use Case**: Powers the "AI Suggest" feature in project creation wizard.
    Helps users discover relevant keywords they might not have considered.
    
    **Request Body**:
    * **research_description**: Natural language description of what you want to research
    * **max_keywords**: Maximum number of keywords to suggest (1-20, default: 10)
    
    **Response**: List of AI-suggested keywords with generation metadata
    
    **Example**: 
    Input: "I want to analyze sentiment about iPhone battery life issues"
    Output: ["battery", "charging", "drain", "power", "life", "performance", "issue", "problem"]
    """
    try:
        suggestions = await ProjectService.suggest_keywords(suggestion_request)
        return suggestions
        
    except ValueError as e:
        error_message = str(e)
        if "not available" in error_message:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "ai_not_available",
                    "message": error_message,
                    "details": {}
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "suggestion_error",
                    "message": error_message,
                    "details": {}
                }
            )
    
    except Exception as e:
        print(f"Unexpected error in suggest_keywords endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while generating keyword suggestions",
                "details": {}
            }
        )
    
@app.post("/ai/subreddits/suggest",
          response_model=SubredditSuggestionResponse,
          responses={
              400: {"model": APIError, "description": "Invalid request or AI unavailable"},
              500: {"model": APIError, "description": "Server error"}
          },
          tags=["ai"],
          summary="Get AI Subreddit Suggestions",
          description="Get AI-powered subreddit suggestions for research topics")
async def suggest_subreddits(suggestion_request: SubredditSuggestionRequest) -> SubredditSuggestionResponse:
    """
    **AI-Powered Subreddit Suggestions**
    
    Get intelligent subreddit suggestions from AI based on your research description.
    
    **How It Works**:
    * Describe what you want to research in natural language
    * AI analyzes your description and suggests relevant subreddit communities
    * Suggestions prioritize relevance first, with larger communities preferred when equally relevant
    * Focuses on active, discussion-rich communities where your research topic would be discussed
    
    **Use Case**: Powers the "AI Suggest" feature in collection creation wizard.
    Helps users discover relevant communities they might not have considered.
    
    **Request Body**:
    * **research_description**: Natural language description of what you want to research
    * **max_subreddits**: Maximum number of subreddits to suggest (1-15, default: 10)
    
    **Response**: List of AI-suggested subreddit names with generation metadata
    
    **Example**: 
    Input: "I want to analyze discussions about electric vehicle charging problems and infrastructure issues"
    Output: ["electricvehicles", "teslamotors", "TeslaModel3", "leaf", "BMW_i3", "Polestar"]
    """
    try:
        suggestions = await ProjectService.suggest_subreddits(suggestion_request)
        return suggestions
        
    except ValueError as e:
        error_message = str(e)
        if "not available" in error_message:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "ai_not_available",
                    "message": error_message,
                    "details": {}
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "suggestion_error",
                    "message": error_message,
                    "details": {}
                }
            )
    
    except Exception as e:
        print(f"Unexpected error in suggest_subreddits endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred while generating subreddit suggestions",
                "details": {}
            }
        )

@app.get("/ai/status",
         response_model=AIStatusResponse,
         responses={500: {"model": APIError}},
         tags=["ai"],
         summary="Get AI System Status",
         description="Get current AI system status and capabilities")
async def get_ai_status() -> AIStatusResponse:
    """
    **AI System Status and Capabilities**
    
    Returns comprehensive information about AI system availability and features.
    
    **Status Information**:
    * Overall AI availability (enabled/disabled)
    * Individual AI provider status (Anthropic, OpenAI, etc.)
    * Available AI features (chat, summaries, keyword suggestions, etc.)
    * Configuration details and model information
    * Embeddings system status for semantic search
    
    **Use Case**: 
    * Frontend can check AI availability before showing AI features
    * Troubleshooting AI configuration issues
    * Displaying AI capabilities to users
    * Determining which features to enable in the UI
    
    **Response**: Complete AI system status with provider details and feature availability
    """
    try:
        status = await ProjectService.get_ai_status()
        return status
        
    except Exception as e:
        print(f"Unexpected error in get_ai_status endpoint: {e}")
        # Return basic unavailable status rather than failing
        return AIStatusResponse(
            ai_available=False,
            providers={},
            features={"keyword_suggestion": False, "summarization": False, "chat_agent": False, "rag_search": False},
            default_provider=None,
            embeddings_info={}
        )
"""
API Data Models

Pydantic models that define the structure of data exchanged between
the frontend and backend. These models serve as contracts and provide
automatic validation and documentation.

Enhanced with Step 4: Chat and AI Feature Models
Enhanced with Step 5: Collection Management Models
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ProjectBase(BaseModel):
    """Base project fields shared between create and response models."""
    name: str = Field(..., description="User-defined project name", min_length=1, max_length=200)
    research_question: Optional[str] = Field(None, description="Business research question driving this analysis", max_length=1000)
    keywords: List[str] = Field(..., description="Keywords to analyze in discussions", min_items=1)
    collection_ids: List[str] = Field(..., description="IDs of Reddit collections to analyze", min_items=1)
    
    @validator('keywords')
    def validate_keywords(cls, v):
        """Ensure keywords are non-empty strings."""
        if not v:
            raise ValueError("At least one keyword is required")
        
        # Remove empty/whitespace-only keywords
        clean_keywords = [kw.strip() for kw in v if kw.strip()]
        if not clean_keywords:
            raise ValueError("Keywords cannot be empty")
        
        return clean_keywords
    
    @validator('name')
    def validate_name(cls, v):
        """Ensure project name is not just whitespace."""
        if not v.strip():
            raise ValueError("Project name cannot be empty")
        return v.strip()


class ProjectCreate(ProjectBase):
    """Data required to create a new project."""
    # Optional configuration settings
    partial_matching: bool = Field(False, description="Use partial keyword matching instead of exact word matching")
    context_window_words: int = Field(5, description="Number of words before/after keyword for sentiment analysis", ge=1, le=50)
    
    # Optional AI features
    generate_summary: bool = Field(False, description="Generate AI summary after analysis completes")


class ProjectStats(BaseModel):
    """Project statistics and metrics."""
    total_mentions: int = Field(0, description="Total keyword mentions found")
    avg_sentiment: float = Field(0.0, description="Average sentiment score (-1.0 to +1.0)")
    keywords_count: int = Field(0, description="Number of keywords analyzed")
    collections_count: int = Field(0, description="Number of collections analyzed")
    posts_analyzed: int = Field(0, description="Number of Reddit posts analyzed")
    comments_analyzed: int = Field(0, description="Number of Reddit comments analyzed")


class ProjectSummary(BaseModel):
    """AI-generated project summary information."""
    summary_text: str = Field(..., description="AI-generated summary of findings")
    summary_preview: str = Field(..., description="First 2-3 sentences for dashboard display")
    generated_at: datetime = Field(..., description="When the summary was generated")
    provider: str = Field(..., description="AI provider used (anthropic, openai, etc.)")
    model: str = Field(..., description="Specific AI model used")


class ProjectResponse(ProjectBase):
    """Complete project data returned by the API."""
    id: str = Field(..., description="Unique project identifier")
    status: str = Field(..., description="Project status: running, completed, failed")
    created_at: datetime = Field(..., description="When the project was created")
    
    # Analysis configuration (included for transparency)
    partial_matching: bool = Field(..., description="Whether partial keyword matching was used")
    context_window_words: int = Field(..., description="Context window size used for sentiment analysis")
    
    # Computed statistics
    stats: ProjectStats = Field(..., description="Project statistics and metrics")
    
    # Optional AI summary (only present if generated)
    summary: Optional[ProjectSummary] = Field(None, description="AI-generated summary if available")
    
    # Collection metadata for frontend display
    collections_metadata: List[Dict[str, Any]] = Field([], description="Metadata about analyzed collections")
    
    # Analysis insights for dashboard cards (only present if analysis completed)
    cooccurrences: Optional[List[Dict[str, Any]]] = Field(None, description="Top keyword co-occurrences")
    trend_summaries: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="Trend direction summaries by keyword")
    sample_contexts: Optional[List[Dict[str, Any]]] = Field(None, description="Sample discussion contexts")
    keywords_data: Optional[List[Dict[str, Any]]] = Field(None, description="Individual keyword statistics with mentions and sentiment")
    
    class Config:
        """Pydantic configuration."""
        # Allow datetime serialization
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        # Example for API documentation
        json_schema_extra = {
            "example": {
                "id": "abc123def",
                "name": "iPhone Battery Life Research",
                "research_question": "What are users saying about iPhone battery life issues?",
                "keywords": ["battery", "drain", "charging", "power"],
                "collection_ids": ["collection-1", "collection-2"],
                "status": "completed",
                "created_at": "2025-01-15T10:30:00Z",
                "partial_matching": False,
                "context_window_words": 5,
                "stats": {
                    "total_mentions": 1247,
                    "avg_sentiment": -0.23,
                    "keywords_count": 4,
                    "collections_count": 2,
                    "posts_analyzed": 156,
                    "comments_analyzed": 892
                },
                "summary": {
                    "summary_text": "Analysis reveals significant user frustration with battery performance...",
                    "summary_preview": "Analysis reveals significant user frustration with battery performance. Key issues include fast draining and slow charging speeds.",
                    "generated_at": "2025-01-15T10:45:00Z",
                    "provider": "anthropic",
                    "model": "claude-3-5-sonnet-20240620"
                },
                "collections_metadata": [
                    {"id": "collection-1", "subreddit": "iphone", "posts_count": 78},
                    {"id": "collection-2", "subreddit": "apple", "posts_count": 78}
                ]
            }
        }


class ProjectListResponse(BaseModel):
    """Response for listing multiple projects (dashboard view)."""
    projects: List[ProjectResponse] = Field(..., description="List of user projects")
    total_count: int = Field(..., description="Total number of projects")
    
    class Config:
        json_schema_extra = {
            "example": {
                "projects": [
                    # ... abbreviated project objects for dashboard
                ],
                "total_count": 5
            }
        }


# ============================================================================
# CHAT AND AI MODELS (EXISTING - STEP 4)
# ============================================================================

class ChatMessageCreate(BaseModel):
    """Request to send a message in a chat session."""
    message: str = Field(..., description="User message to send to AI", min_length=1, max_length=2000)
    search_type: str = Field("auto", description="Search method for AI to use: auto, keyword, local_semantic, cloud_semantic, analytics_driven")
    
    @validator('message')
    def validate_message(cls, v):
        """Ensure message is not just whitespace."""
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()
    
    @validator('search_type')
    def validate_search_type(cls, v):
        """Validate search type options."""
        valid_types = ["auto", "keyword", "local_semantic", "cloud_semantic", "analytics_driven"]
        if v not in valid_types:
            raise ValueError(f"Search type must be one of: {valid_types}")
        return v


class ChatMessage(BaseModel):
    """Individual chat message with metadata."""
    id: int = Field(..., description="Unique message ID")
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="When the message was sent")
    tokens_used: int = Field(0, description="Tokens used for this message (assistant only)")
    cost_estimate: float = Field(0.0, description="Estimated cost for this message (assistant only)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        json_schema_extra = {
            "example": {
                "id": 12345,
                "role": "assistant",
                "content": "Based on your analysis, users frequently mention battery drain issues with negative sentiment...",
                "timestamp": "2025-01-15T10:45:30Z",
                "tokens_used": 245,
                "cost_estimate": 0.0012
            }
        }


class ChatResponse(BaseModel):
    """Response from sending a chat message."""
    message: str = Field(..., description="AI assistant's response")
    sources: List[Dict[str, Any]] = Field([], description="Source attributions for the response")
    analytics_insights: Dict[str, Any] = Field({}, description="Analytics data used in the response")
    search_type: str = Field(..., description="Search method that was used")
    discussions_found: int = Field(0, description="Number of discussions found for the response")
    tokens_used: int = Field(0, description="Tokens used for this response")
    cost_estimate: float = Field(0.0, description="Estimated cost for this response")
    session_id: str = Field(..., description="Chat session ID")
    query_classification: Dict[str, Any] = Field({}, description="How the query was classified and routed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Based on your analysis of battery-related discussions, I found significant negative sentiment around charging issues...",
                "sources": [
                    {
                        "content_id": "abc123",
                        "content_type": "post",
                        "relevance_score": 0.85
                    }
                ],
                "analytics_insights": {
                    "battery": {
                        "total_mentions": 245,
                        "avg_sentiment": -0.34
                    }
                },
                "search_type": "analytics_driven",
                "discussions_found": 3,
                "tokens_used": 245,
                "cost_estimate": 0.0012,
                "session_id": "chat_session_123",
                "query_classification": {
                    "type": "analytics",
                    "confidence": 0.9
                }
            }
        }


class ChatSessionInfo(BaseModel):
    """Information about a chat session."""
    session_id: str = Field(..., description="Unique chat session identifier")
    created_at: datetime = Field(..., description="When the chat session was created")
    last_active: datetime = Field(..., description="When the session was last used")
    message_count: int = Field(0, description="Number of messages in the session")
    preview: str = Field("", description="Preview of the conversation (first user message)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        json_schema_extra = {
            "example": {
                "session_id": "chat_session_123",
                "created_at": "2025-01-15T10:30:00Z",
                "last_active": "2025-01-15T10:45:00Z",
                "message_count": 8,
                "preview": "What do people think about battery life?"
            }
        }


class ChatSessionListResponse(BaseModel):
    """Response for listing chat sessions."""
    sessions: List[ChatSessionInfo] = Field(..., description="List of chat sessions for the project")
    total_count: int = Field(..., description="Total number of chat sessions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sessions": [
                    {
                        "session_id": "chat_session_123",
                        "created_at": "2025-01-15T10:30:00Z",
                        "last_active": "2025-01-15T10:45:00Z",
                        "message_count": 8,
                        "preview": "What do people think about battery life?"
                    }
                ],
                "total_count": 3
            }
        }


class ChatHistoryResponse(BaseModel):
    """Response for retrieving chat history."""
    messages: List[ChatMessage] = Field(..., description="Chat messages in chronological order")
    session_id: str = Field(..., description="Chat session ID")
    total_messages: int = Field(..., description="Total number of messages in the session")
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {
                        "id": 1,
                        "role": "user",
                        "content": "What do people think about battery life?",
                        "timestamp": "2025-01-15T10:30:00Z",
                        "tokens_used": 0,
                        "cost_estimate": 0.0
                    },
                    {
                        "id": 2,
                        "role": "assistant",
                        "content": "Based on your analysis...",
                        "timestamp": "2025-01-15T10:30:15Z",
                        "tokens_used": 245,
                        "cost_estimate": 0.0012
                    }
                ],
                "session_id": "chat_session_123",
                "total_messages": 2
            }
        }


class KeywordSuggestionRequest(BaseModel):
    """Request for AI keyword suggestions."""
    research_description: str = Field(..., description="Description of what you want to research", min_length=1, max_length=1000)
    max_keywords: int = Field(10, description="Maximum number of keywords to suggest", ge=1, le=20)
    
    @validator('research_description')
    def validate_research_description(cls, v):
        """Ensure research description is not just whitespace."""
        if not v.strip():
            raise ValueError("Research description cannot be empty")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "research_description": "I want to analyze sentiment about iPhone battery life issues and charging problems",
                "max_keywords": 8
            }
        }


class KeywordSuggestionResponse(BaseModel):
    """Response with AI-suggested keywords."""
    keywords: List[str] = Field(..., description="AI-suggested keywords for the research topic")
    research_description: str = Field(..., description="Original research description")
    provider: str = Field(..., description="AI provider used for suggestions")
    model: str = Field(..., description="AI model used")
    tokens_used: int = Field(0, description="Tokens used for generation")
    cost_estimate: float = Field(0.0, description="Estimated cost for this request")
    
    class Config:
        json_schema_extra = {
            "example": {
                "keywords": ["battery", "charging", "drain", "power", "life", "performance", "issue", "problem"],
                "research_description": "I want to analyze sentiment about iPhone battery life issues and charging problems",
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-20240620",
                "tokens_used": 125,
                "cost_estimate": 0.0006
            }
        }


class AIStatusResponse(BaseModel):
    """Response about AI system status and capabilities."""
    ai_available: bool = Field(..., description="Whether AI features are available")
    providers: Dict[str, Dict[str, Any]] = Field(..., description="Status of each AI provider")
    features: Dict[str, bool] = Field(..., description="Available AI features")
    default_provider: Optional[str] = Field(None, description="Default AI provider name")
    embeddings_info: Dict[str, Any] = Field({}, description="Embeddings system status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ai_available": True,
                "providers": {
                    "anthropic": {
                        "available": True,
                        "model": "claude-3-5-sonnet-20240620",
                        "status": "Connected successfully"
                    },
                    "openai": {
                        "available": True,
                        "model": "gpt-4o",
                        "status": "Connected successfully"
                    }
                },
                "features": {
                    "keyword_suggestion": True,
                    "summarization": True,
                    "chat_agent": True,
                    "rag_search": True
                },
                "default_provider": "anthropic",
                "embeddings_info": {
                    "provider": "openai",
                    "model": "text-embedding-3-small",
                    "available": True
                }
            }
        }


# ============================================================================
# INDEXING MODELS (NEW - FOR SEMANTIC SEARCH)
# ============================================================================

class IndexingRequest(BaseModel):
    """Request to start content indexing for semantic search."""
    provider_type: str = Field(..., description="Embedding provider to use", pattern="^(local|openai)$")
    force_reindex: bool = Field(False, description="Force reindexing even if already indexed")
    
    @validator('provider_type')
    def validate_provider_type(cls, v):
        """Validate provider type options."""
        valid_types = ["local", "openai"]
        if v not in valid_types:
            raise ValueError(f"Provider type must be one of: {valid_types}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider_type": "local",
                "force_reindex": False
            }
        }


class IndexingResponse(BaseModel):
    """Response from starting content indexing."""
    status: str = Field(..., description="Indexing status: started, already_indexed")
    message: str = Field(..., description="Human-readable status message")
    provider_type: str = Field(..., description="Embedding provider being used")
    estimated_duration_minutes: int = Field(..., description="Estimated time to completion")
    total_content_items: int = Field(..., description="Total number of items to index")
    started_at: datetime = Field(..., description="When indexing started")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        json_schema_extra = {
            "example": {
                "status": "started",
                "message": "Indexing started successfully with local embeddings",
                "provider_type": "local",
                "estimated_duration_minutes": 5,
                "total_content_items": 1247,
                "started_at": "2025-01-15T10:30:00Z"
            }
        }


class IndexingStatusResponse(BaseModel):
    """Response for indexing status and search capabilities."""
    indexing_status: Dict[str, str] = Field(..., description="Status of each indexing type")
    search_capabilities: Dict[str, bool] = Field(..., description="Available search types")
    total_content_items: int = Field(..., description="Total content items in project")
    local_indexed: int = Field(0, description="Items indexed with local embeddings")
    cloud_indexed: int = Field(0, description="Items indexed with cloud embeddings")
    current_indexing: Optional[Dict[str, Any]] = Field(None, description="Currently running indexing job")
    
    class Config:
        json_schema_extra = {
            "example": {
                "indexing_status": {
                    "local": "complete",
                    "cloud": "none"
                },
                "search_capabilities": {
                    "keyword": True,
                    "local_semantic": True,
                    "cloud_semantic": False,
                    "analytics_driven": True
                },
                "total_content_items": 1247,
                "local_indexed": 1247,
                "cloud_indexed": 0,
                "current_indexing": None
            }
        }



# ============================================================================
# COLLECTION MANAGEMENT MODELS (NEW - STEP 5)
# ============================================================================

class CollectionParams(BaseModel):
    """Collection parameters for Reddit data collection."""
    sort_method: str = Field(..., description="Sort method for posts", pattern="^(hot|new|rising|top|controversial)$")
    time_period: Optional[str] = Field(None, description="Time period for top/controversial", pattern="^(hour|day|week|month|year|all)$")
    posts_count: int = Field(..., description="Number of posts to collect", ge=1, le=1000)
    root_comments: int = Field(..., description="Max root comments per post", ge=0, le=100)
    replies_per_root: int = Field(..., description="Max replies per root comment", ge=0, le=50)
    min_upvotes: int = Field(..., description="Minimum upvotes for comments", ge=0)
    
    @validator('time_period')
    def validate_time_period(cls, v, values):
        """Validate time period is provided for top/controversial sorts."""
        sort_method = values.get('sort_method')
        if sort_method in ['top', 'controversial'] and not v:
            raise ValueError(f"Time period is required for sort method '{sort_method}'")
        if sort_method not in ['top', 'controversial'] and v:
            raise ValueError(f"Time period should not be provided for sort method '{sort_method}'")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "sort_method": "hot",
                "time_period": None,
                "posts_count": 50,
                "root_comments": 10,
                "replies_per_root": 3,
                "min_upvotes": 1
            }
        }


class CollectionCreateRequest(BaseModel):
    """Request to create one or more collections."""
    subreddits: List[str] = Field(..., description="List of subreddit names (without r/)", min_items=1, max_items=10)
    collection_params: CollectionParams = Field(..., description="Collection parameters to apply to all subreddits")
    
    @validator('subreddits')
    def validate_subreddits(cls, v):
        """Validate subreddit names."""
        if not v:
            raise ValueError("At least one subreddit is required")
        
        clean_subreddits = []
        for subreddit in v:
            subreddit = subreddit.strip()
            if not subreddit:
                raise ValueError("Subreddit names cannot be empty")
            
            # Remove r/ prefix if present
            if subreddit.startswith('r/'):
                subreddit = subreddit[2:]
            
            # Basic validation of subreddit name format
            if not subreddit.replace('_', 'a').replace('-', 'a').isalnum():
                raise ValueError(f"Invalid subreddit name format: {subreddit}")
            
            clean_subreddits.append(subreddit)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_subreddits = []
        for sub in clean_subreddits:
            if sub.lower() not in seen:
                seen.add(sub.lower())
                unique_subreddits.append(sub)
        
        return unique_subreddits
    
    class Config:
        json_schema_extra = {
            "example": {
                "subreddits": ["iphone", "apple", "ios"],
                "collection_params": {
                    "sort_method": "hot",
                    "time_period": None,
                    "posts_count": 50,
                    "root_comments": 10,
                    "replies_per_root": 3,
                    "min_upvotes": 1
                }
            }
        }


class CollectionResponse(BaseModel):
    """Individual collection metadata and status."""
    id: str = Field(..., description="Unique collection identifier")
    subreddit: str = Field(..., description="Subreddit name")
    sort_method: str = Field(..., description="Sort method used")
    time_period: Optional[str] = Field(None, description="Time period used (if applicable)")
    posts_requested: int = Field(..., description="Number of posts requested")
    posts_collected: int = Field(0, description="Number of posts actually collected")
    comments_collected: int = Field(0, description="Number of comments collected")
    status: str = Field(..., description="Collection status: running, completed, failed")
    created_at: datetime = Field(..., description="When the collection was created")
    error_message: Optional[str] = Field(None, description="Error message if collection failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        json_schema_extra = {
            "example": {
                "id": "collection-abc123",
                "subreddit": "iphone",
                "sort_method": "hot",
                "time_period": None,
                "posts_requested": 50,
                "posts_collected": 47,
                "comments_collected": 312,
                "status": "completed",
                "created_at": "2025-01-15T10:30:00Z",
                "error_message": None
            }
        }


class CollectionBatchResponse(BaseModel):
    """Response from creating a batch of collections."""
    batch_id: str = Field(..., description="Unique batch identifier for progress tracking")
    collection_ids: List[str] = Field(..., description="List of individual collection IDs created")
    subreddits: List[str] = Field(..., description="List of subreddits being collected")
    status: str = Field(..., description="Batch status: started, running, completed, failed")
    started_at: datetime = Field(..., description="When the batch collection started")
    estimated_duration_minutes: int = Field(..., description="Estimated time to completion")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        json_schema_extra = {
            "example": {
                "batch_id": "batch-xyz789",
                "collection_ids": ["collection-abc123", "collection-def456", "collection-ghi789"],
                "subreddits": ["iphone", "apple", "ios"],
                "status": "started",
                "started_at": "2025-01-15T10:30:00Z",
                "estimated_duration_minutes": 15
            }
        }


class CollectionBatchStatusResponse(BaseModel):
    """Response for collection batch progress tracking."""
    batch_id: str = Field(..., description="Batch identifier")
    status: str = Field(..., description="Overall batch status")
    progress_percentage: int = Field(..., description="Overall completion percentage (0-100)")
    current_subreddit: Optional[str] = Field(None, description="Currently processing subreddit")
    completed_subreddits: List[str] = Field([], description="List of completed subreddits")
    failed_subreddits: List[str] = Field([], description="List of failed subreddits")
    collections: List[CollectionResponse] = Field(..., description="Individual collection statuses")
    started_at: datetime = Field(..., description="When the batch started")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        json_schema_extra = {
            "example": {
                "batch_id": "batch-xyz789",
                "status": "running",
                "progress_percentage": 67,
                "current_subreddit": "ios",
                "completed_subreddits": ["iphone", "apple"],
                "failed_subreddits": [],
                "collections": [
                    {
                        "id": "collection-abc123",
                        "subreddit": "iphone",
                        "status": "completed",
                        "posts_collected": 47,
                        "comments_collected": 312
                    }
                ],
                "started_at": "2025-01-15T10:30:00Z",
                "estimated_completion": "2025-01-15T10:45:00Z"
            }
        }


class CollectionListResponse(BaseModel):
    """Response for listing collections."""
    collections: List[CollectionResponse] = Field(..., description="List of collections")
    total_count: int = Field(..., description="Total number of collections")
    
    class Config:
        json_schema_extra = {
            "example": {
                "collections": [
                    {
                        "id": "collection-abc123",
                        "subreddit": "iphone",
                        "sort_method": "hot",
                        "posts_requested": 50,
                        "posts_collected": 47,
                        "status": "completed",
                        "created_at": "2025-01-15T10:30:00Z"
                    }
                ],
                "total_count": 15
            }
        }


class APIError(BaseModel):
    """Standard error response format."""
    error: str = Field(..., description="Error type or category")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "validation_error",
                "message": "Project name cannot be empty",
                "details": {"field": "name", "value": ""}
            }
        }

# ============================================================================
# CONTEXT FILTERING MODELS (UPDATED FOR CONTENT-CENTRIC AGGREGATION)
# ============================================================================

class ContextFilters(BaseModel):
    """Request filters for context exploration."""
    primary_keyword: Optional[str] = Field(None, description="Primary keyword to filter by (optional - if not provided, shows all keywords)")
    secondary_keyword: Optional[str] = Field(None, description="Secondary keyword for co-occurrence filtering")
    min_sentiment: float = Field(-1.0, description="Minimum sentiment score", ge=-1.0, le=1.0)
    max_sentiment: float = Field(1.0, description="Maximum sentiment score", ge=-1.0, le=1.0)
    sort_by: str = Field("newest", description="Sort order: newest, oldest, sentiment_asc, sentiment_desc")
    
    @validator('max_sentiment')
    def validate_sentiment_range(cls, v, values):
        """Ensure max_sentiment >= min_sentiment."""
        if 'min_sentiment' in values and v < values['min_sentiment']:
            raise ValueError("max_sentiment must be greater than or equal to min_sentiment")
        return v
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        """Validate sort_by options."""
        valid_options = ["newest", "oldest", "sentiment_asc", "sentiment_desc"]
        if v not in valid_options:
            raise ValueError(f"sort_by must be one of: {valid_options}")
        return v

class KeywordMentionDetail(BaseModel):
    """Individual keyword mention with position and sentiment."""
    keyword: str = Field(..., description="The keyword that was found")
    position_in_content: int = Field(..., description="Character position of keyword in content")
    sentiment_score: float = Field(..., description="Sentiment score for this specific keyword mention")

class ContextInstance(BaseModel):
    """Aggregated context instance with all keyword mentions consolidated."""
    content_type: str = Field(..., description="Type of content: post or comment")
    content_reddit_id: str = Field(..., description="Reddit ID of the content")
    collection_id: str = Field(..., description="Collection ID the content belongs to")
    context: str = Field(..., description="Full context text")
    avg_sentiment_score: float = Field(..., description="Average sentiment score across filtered keywords")
    created_utc: int = Field(..., description="Unix timestamp when content was created")
    keyword_mentions: List[KeywordMentionDetail] = Field(..., description="All keyword mentions in this content piece")
    parent_post_id: Optional[str] = Field(None, description="Reddit ID of parent post (for comments only)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_type": "post",
                "content_reddit_id": "abc123",
                "collection_id": "collection-xyz",
                "context": "My iPhone battery drains so fast when charging...",
                "avg_sentiment_score": -0.65,
                "created_utc": 1640995200,
                "keyword_mentions": [
                    {
                        "keyword": "battery",
                        "position_in_content": 10,
                        "sentiment_score": -0.6
                    },
                    {
                        "keyword": "charging",
                        "position_in_content": 45,
                        "sentiment_score": -0.7
                    }
                ]
            }
        }

class PaginationInfo(BaseModel):
    """Pagination metadata."""
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total_count: int = Field(..., description="Total number of matching contexts")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")

class FilteredContextsResponse(BaseModel):
    """Response for filtered context exploration with content consolidation."""
    contexts: List[ContextInstance] = Field(..., description="List of aggregated context instances")
    pagination: PaginationInfo = Field(..., description="Pagination information")
    filters_applied: Dict[str, Any] = Field(..., description="Filters that were applied")
    
    class Config:
        json_schema_extra = {
            "example": {
                "contexts": [
                    {
                        "content_type": "post",
                        "content_reddit_id": "abc123",
                        "collection_id": "collection-xyz",
                        "context": "My iPhone battery drains so fast when charging...",
                        "avg_sentiment_score": -0.65,
                        "created_utc": 1640995200,
                        "keyword_mentions": [
                            {
                                "keyword": "battery",
                                "position_in_content": 10,
                                "sentiment_score": -0.6
                            },
                            {
                                "keyword": "charging",
                                "position_in_content": 45,
                                "sentiment_score": -0.7
                            }
                        ]
                    }
                ],
                "pagination": {
                    "page": 1,
                    "limit": 20,
                    "total_count": 156,
                    "total_pages": 8,
                    "has_next": True,
                    "has_previous": False
                },
                "filters_applied": {
                    "primary_keyword": "battery",
                    "secondary_keyword": "charging",
                    "sentiment_range": [-1.0, 1.0],
                    "sort_by": "newest"
                }
            }
        }
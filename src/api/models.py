"""
API Data Models

Pydantic models that define the structure of data exchanged between
the frontend and backend. These models serve as contracts and provide
automatic validation and documentation.

Enhanced with Step 4: Chat and AI Feature Models
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
    
    class Config:
        """Pydantic configuration."""
        # Allow datetime serialization
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        # Example for API documentation
        schema_extra = {
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
        schema_extra = {
            "example": {
                "projects": [
                    # ... abbreviated project objects for dashboard
                ],
                "total_count": 5
            }
        }


# ============================================================================
# CHAT AND AI MODELS (NEW - STEP 4)
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
        
        schema_extra = {
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
        schema_extra = {
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
        
        schema_extra = {
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
        schema_extra = {
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
        schema_extra = {
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
        schema_extra = {
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
        schema_extra = {
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
        schema_extra = {
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


class AIExplanationRequest(BaseModel):
    """Request for AI explanation of analysis results."""
    topic: str = Field(..., description="Topic or aspect to explain", min_length=1, max_length=200)
    context: Optional[str] = Field(None, description="Additional context for the explanation", max_length=500)
    
    @validator('topic')
    def validate_topic(cls, v):
        """Ensure topic is not just whitespace."""
        if not v.strip():
            raise ValueError("Topic cannot be empty")
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "negative sentiment around charging",
                "context": "I see that charging-related keywords have very negative sentiment but want to understand why"
            }
        }


class AIExplanationResponse(BaseModel):
    """Response with AI explanation of analysis results."""
    explanation: str = Field(..., description="AI-generated explanation")
    topic: str = Field(..., description="Original topic that was explained")
    related_insights: List[str] = Field([], description="Related insights or suggestions")
    sources_used: List[Dict[str, Any]] = Field([], description="Data sources used for the explanation")
    provider: str = Field(..., description="AI provider used")
    model: str = Field(..., description="AI model used")
    tokens_used: int = Field(0, description="Tokens used for generation")
    cost_estimate: float = Field(0.0, description="Estimated cost for this request")
    
    class Config:
        schema_extra = {
            "example": {
                "explanation": "The negative sentiment around charging appears to stem from two main issues: slow charging speeds and inconsistent charging behavior...",
                "topic": "negative sentiment around charging",
                "related_insights": [
                    "Fast charging concerns are mentioned 3x more than slow charging",
                    "Charging issues correlate with battery age discussions"
                ],
                "sources_used": [
                    {
                        "keyword": "charging",
                        "mentions": 342,
                        "avg_sentiment": -0.45
                    }
                ],
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-20240620",
                "tokens_used": 287,
                "cost_estimate": 0.0014
            }
        }


class APIError(BaseModel):
    """Standard error response format."""
    error: str = Field(..., description="Error type or category")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "validation_error",
                "message": "Project name cannot be empty",
                "details": {"field": "name", "value": ""}
            }
        }
"""
API Data Models

Pydantic models that define the structure of data exchanged between
the frontend and backend. These models serve as contracts and provide
automatic validation and documentation.
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
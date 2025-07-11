"""
API Service Layer

Business logic and data transformation functions for API endpoints.
Handles the complex work of converting between backend data structures
and frontend-friendly API responses.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from src.analytics import analytics_engine
from src.database import db
from src.llm.services.summarizer import analysis_summarizer
from .models import ProjectResponse, ProjectStats, ProjectSummary, ProjectCreate


class ProjectService:
    """Service class for project-related operations."""
    
    @staticmethod
    async def get_all_projects() -> List[ProjectResponse]:
        """
        Get all projects with full metadata for dashboard display.
        
        Returns:
            List of ProjectResponse objects ready for frontend consumption
        """
        try:
            # Get all analysis sessions from database
            analysis_sessions = db.get_analysis_sessions()
            
            # Transform each session into a ProjectResponse
            projects = []
            for session in analysis_sessions:
                project = await ProjectService._transform_session_to_project(session)
                projects.append(project)
            
            # Sort by creation date (newest first)
            projects.sort(key=lambda p: p.created_at, reverse=True)
            
            return projects
            
        except Exception as e:
            print(f"Error in ProjectService.get_all_projects: {e}")
            return []
    
    @staticmethod
    async def get_project_by_id(project_id: str) -> Optional[ProjectResponse]:
        """
        Get a specific project by ID.
        
        Args:
            project_id: Project ID to retrieve
            
        Returns:
            ProjectResponse object or None if not found
        """
        try:
            # Get specific analysis session
            analysis_session = db.get_analysis_session(project_id)
            if not analysis_session:
                return None
            
            # Transform to ProjectResponse format
            project = await ProjectService._transform_session_to_project(analysis_session)
            return project
            
        except Exception as e:
            print(f"Error in ProjectService.get_project_by_id: {e}")
            return None
    
    @staticmethod
    async def create_project(project_data: ProjectCreate) -> ProjectResponse:
        """
        Create a new research project.
        
        Args:
            project_data: ProjectCreate object with project details
            
        Returns:
            ProjectResponse for the newly created project
            
        Raises:
            ValueError: If validation fails or project creation fails
        """
        try:
            # Validate that collections exist
            ProjectService._validate_collections_exist(project_data.collection_ids)
            
            # Create analysis session using existing backend
            session_id = analytics_engine.create_session(
                name=project_data.name,
                keywords=project_data.keywords,
                collection_ids=project_data.collection_ids,
                partial_matching=project_data.partial_matching,
                context_window_words=project_data.context_window_words
            )
            
            # Get the newly created session
            analysis_session = db.get_analysis_session(session_id)
            if not analysis_session:
                raise ValueError(f"Failed to retrieve created session: {session_id}")
            
            # Transform to ProjectResponse format
            project = await ProjectService._transform_session_to_project(analysis_session)
            
            return project
            
        except ValueError as e:
            # Re-raise validation errors
            raise e
        except Exception as e:
            # Log unexpected errors and convert to ValueError
            print(f"Error in ProjectService.create_project: {e}")
            raise ValueError(f"Failed to create project: {str(e)}")
    
    @staticmethod
    async def delete_project(project_id: str) -> bool:
        """
        Delete a project and all its associated data.
        
        Args:
            project_id: Project ID to delete
            
        Returns:
            True if deletion successful, False if project not found
            
        Raises:
            ValueError: If deletion fails due to server error
        """
        try:
            # Check if project exists first
            analysis_session = db.get_analysis_session(project_id)
            if not analysis_session:
                return False
            
            # Delete the analysis session (and all related data)
            success = analytics_engine.delete_session(project_id)
            
            if not success:
                raise ValueError(f"Failed to delete project: {project_id}")
            
            return True
            
        except ValueError as e:
            # Re-raise deletion errors
            raise e
        except Exception as e:
            # Log unexpected errors and convert to ValueError
            print(f"Error in ProjectService.delete_project: {e}")
            raise ValueError(f"Failed to delete project: {str(e)}")
    
    @staticmethod
    async def _transform_session_to_project(session) -> ProjectResponse:
        """
        Transform an AnalysisSession into a ProjectResponse.
        
        Args:
            session: AnalysisSession object from database
            
        Returns:
            ProjectResponse ready for API consumption
        """
        # Parse JSON fields from database
        keywords = json.loads(session.keywords)
        collection_ids = json.loads(session.collection_ids)
        
        # Create stats object
        stats = ProjectService._calculate_project_stats(session, keywords, collection_ids)
        
        # Try to get AI summary if it exists
        summary = await ProjectService._get_project_summary(session.id)
        
        # Get collections metadata
        collections_metadata = ProjectService._get_collections_metadata(collection_ids)
        
        # Convert created_at timestamp to datetime
        created_at = datetime.fromtimestamp(session.created_at)
        
        return ProjectResponse(
            id=session.id,
            name=session.name,
            research_question=None,  # We don't store this yet - will add in future
            keywords=keywords,
            collection_ids=collection_ids,
            status=session.status,
            created_at=created_at,
            partial_matching=session.partial_matching,
            context_window_words=session.context_window_words,
            stats=stats,
            summary=summary,
            collections_metadata=collections_metadata
        )
    
    @staticmethod
    def _calculate_project_stats(session, keywords: List[str], collection_ids: List[str]) -> ProjectStats:
        """Calculate project statistics from session data."""
        return ProjectStats(
            total_mentions=session.total_mentions or 0,
            avg_sentiment=session.avg_sentiment or 0.0,
            keywords_count=len(keywords),
            collections_count=len(collection_ids),
            posts_analyzed=0,  # Could add logic to count actual posts if needed
            comments_analyzed=0  # Could add logic to count actual comments if needed
        )
    
    @staticmethod
    async def _get_project_summary(session_id: str) -> Optional[ProjectSummary]:
        """
        Get AI summary for a project if it exists.
        
        Args:
            session_id: Analysis session ID
            
        Returns:
            ProjectSummary object or None if no summary exists
        """
        try:
            summary_data = analysis_summarizer.get_existing_summary(session_id)
            if not summary_data:
                return None
            
            # Create preview (first 2-3 sentences)
            full_text = summary_data['summary']
            sentences = full_text.split('. ')
            preview = '. '.join(sentences[:2]) + '.' if len(sentences) >= 2 else full_text
            
            # Truncate preview if too long
            if len(preview) > 200:
                preview = preview[:197] + "..."
            
            # Parse the generated_at timestamp
            generated_at_str = summary_data['metadata']['generated_at']
            if generated_at_str.endswith('Z'):
                generated_at_str = generated_at_str.replace('Z', '+00:00')
            generated_at = datetime.fromisoformat(generated_at_str)
            
            return ProjectSummary(
                summary_text=full_text,
                summary_preview=preview,
                generated_at=generated_at,
                provider=summary_data['metadata']['provider'],
                model=summary_data['metadata']['model']
            )
            
        except Exception as e:
            print(f"Could not get summary for session {session_id}: {e}")
            return None
    
    @staticmethod
    def _get_collections_metadata(collection_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get metadata about collections for frontend display.
        
        Args:
            collection_ids: List of collection IDs to get metadata for
            
        Returns:
            List of collection metadata dictionaries
        """
        try:
            collections_metadata = []
            collections = db.get_collections()
            
            for collection in collections:
                if collection.id in collection_ids:
                    collections_metadata.append({
                        "id": collection.id,
                        "subreddit": collection.subreddit,
                        "sort_method": collection.sort_method,
                        "time_period": collection.time_period,
                        "created_at": datetime.fromtimestamp(collection.created_at).isoformat(),
                        "status": collection.status,
                        "posts_requested": collection.posts_requested
                    })
            
            return collections_metadata
            
        except Exception as e:
            print(f"Error getting collections metadata: {e}")
            return []
    
    @staticmethod
    def _validate_collections_exist(collection_ids: List[str]) -> None:
        """
        Validate that all specified collection IDs exist.
        
        Args:
            collection_ids: List of collection IDs to validate
            
        Raises:
            ValueError: If any collection ID doesn't exist
        """
        try:
            existing_collections = db.get_collections()
            existing_ids = {collection.id for collection in existing_collections}
            
            missing_ids = []
            for collection_id in collection_ids:
                if collection_id not in existing_ids:
                    missing_ids.append(collection_id)
            
            if missing_ids:
                raise ValueError(f"Collection(s) not found: {', '.join(missing_ids)}")
                
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"Failed to validate collections: {str(e)}")
"""
API Service Layer

Business logic and data transformation functions for API endpoints.
Handles the complex work of converting between backend data structures
and frontend-friendly API responses.

Enhanced with Step 3: Analysis Workflow Management
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import BackgroundTasks
import json

from src.analytics import analytics_engine
from src.database import db
from src.llm.services.summarizer import analysis_summarizer
from src.llm import is_llm_available
from .models import ProjectResponse, ProjectStats, ProjectSummary, ProjectCreate

# Temporary in-memory storage for project preferences
_project_preferences = {}


class ProjectService:
    """Service class for project-related operations with analysis workflow management."""
    
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
        """Create a new research project."""
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
        
            # Store the generate_summary preference for this project
            _project_preferences[session_id] = {
                'generate_summary': project_data.generate_summary
            }
        
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
        """Delete a project and all its associated data."""
        try:
            # Check if project exists first
            analysis_session = db.get_analysis_session(project_id)
            if not analysis_session:
                return False
        
            # Delete the analysis session (and all related data)
            success = analytics_engine.delete_session(project_id)
        
            if not success:
                raise ValueError(f"Failed to delete project: {project_id}")
        
            # Clean up any stored preferences
            _project_preferences.pop(project_id, None)
        
            return True
            
        except ValueError as e:
            # Re-raise deletion errors
            raise e
        except Exception as e:
            # Log unexpected errors and convert to ValueError
            print(f"Error in ProjectService.delete_project: {e}")
            raise ValueError(f"Failed to delete project: {str(e)}")
    
    # ============================================================================
    # ANALYSIS WORKFLOW METHODS (NEW - STEP 3)
    # ============================================================================
    
    @staticmethod
    async def start_analysis(project_id: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """Start analysis processing for a project using background tasks."""
        try:
            # Get and validate analysis session
            analysis_session = db.get_analysis_session(project_id)
            if not analysis_session:
                raise ValueError(f"Project not found: {project_id}")
        
            # Check if analysis is already running or completed
            if analysis_session.status == 'running':
                raise ValueError(f"Analysis is already running for project: {project_id}")
        
            # Note: Allow re-running completed analyses for flexibility
            # Users might want to re-analyze with updated data or different parameters
        
            # Reset session status to running
            db.update_analysis_session_status(project_id, 'running')
        
            # Get the user's generate_summary preference from project creation
            preferences = _project_preferences.get(project_id, {})
            generate_summary = preferences.get('generate_summary', False)
        
            # Start background analysis task with stored preference
            background_tasks.add_task(
                ProjectService._run_background_analysis,
                project_id,
                analysis_session,
                generate_summary
            )
            
            # Return immediate confirmation
            return {
                "status": "started",
                "project_id": project_id,
                "message": "Analysis started successfully",
                "estimated_duration_minutes": ProjectService._estimate_analysis_duration(analysis_session),
                "started_at": datetime.utcnow().isoformat(),
                "analysis_phases": [
                    "Data Processing",
                    "Keyword Analysis", 
                    "Sentiment Analysis",
                    "Co-occurrence Analysis",
                    "AI Summary Generation" if is_llm_available() else None
                ]
            }
            
        except ValueError as e:
            # Re-raise validation errors
            raise e
        except Exception as e:
            # Log unexpected errors and convert to ValueError
            print(f"Error in ProjectService.start_analysis: {e}")
            raise ValueError(f"Failed to start analysis: {str(e)}")
    
    @staticmethod
    async def get_analysis_status(project_id: str) -> Dict[str, Any]:
        """
        Get current analysis status and progress for a project.
        
        Args:
            project_id: Project ID to check status for
            
        Returns:
            Dictionary with comprehensive status information
            
        Raises:
            ValueError: If project not found
        """
        try:
            # Get analysis session
            analysis_session = db.get_analysis_session(project_id)
            if not analysis_session:
                raise ValueError(f"Project not found: {project_id}")
            
            # Get basic status information
            status_info = {
                "project_id": project_id,
                "status": analysis_session.status,
                "created_at": datetime.fromtimestamp(analysis_session.created_at).isoformat(),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Add status-specific information
            if analysis_session.status == 'running':
                # For running analysis, provide progress estimates
                progress_info = ProjectService._get_analysis_progress(analysis_session)
                status_info.update(progress_info)
                
            elif analysis_session.status == 'completed':
                # For completed analysis, provide summary statistics
                completion_info = ProjectService._get_completion_info(analysis_session)
                status_info.update(completion_info)
                
            elif analysis_session.status == 'failed':
                # For failed analysis, provide error information
                error_info = ProjectService._get_error_info(analysis_session)
                status_info.update(error_info)
            
            return status_info
            
        except ValueError as e:
            # Re-raise validation errors
            raise e
        except Exception as e:
            # Log unexpected errors and convert to ValueError
            print(f"Error in ProjectService.get_analysis_status: {e}")
            raise ValueError(f"Failed to get analysis status: {str(e)}")
    
    @staticmethod
    async def get_analysis_results(project_id: str) -> ProjectResponse:
        """
        Get complete analysis results for a project.
        
        Args:
            project_id: Project ID to get results for
            
        Returns:
            ProjectResponse with complete analysis results
            
        Raises:
            ValueError: If project not found or analysis not completed
        """
        try:
            # Get analysis session
            analysis_session = db.get_analysis_session(project_id)
            if not analysis_session:
                raise ValueError(f"Project not found: {project_id}")
            
            # Check if analysis is completed
            if analysis_session.status != 'completed':
                raise ValueError(f"Analysis not completed for project: {project_id}. Current status: {analysis_session.status}")
            
            # Get comprehensive results using existing backend
            session_results = analytics_engine.get_session_results_with_summary(project_id)
            
            # Transform to ProjectResponse format with enhanced results
            project = await ProjectService._transform_session_to_project_with_results(
                analysis_session, session_results
            )
            
            return project
            
        except ValueError as e:
            # Re-raise validation errors
            raise e
        except Exception as e:
            # Log unexpected errors and convert to ValueError
            print(f"Error in ProjectService.get_analysis_results: {e}")
            raise ValueError(f"Failed to get analysis results: {str(e)}")
    
    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================
    
    @staticmethod
    async def _run_background_analysis(project_id: str, analysis_session, 
                                  generate_summary: bool = False):
        """Run analysis in background task with user preference."""
        try:
            print(f"🚀 Starting background analysis for project: {project_id}")
        
            # Use user preference from project creation AND check if LLM is available
            should_generate_summary = generate_summary and is_llm_available()
        
            if should_generate_summary:
                print(f"📊 Running analysis with AI summary for project: {project_id}")
                analytics_engine.run_analysis_with_summary(
                    session_id=project_id,
                    generate_summary=True
                )
            else:
                reason = "user disabled" if not generate_summary else "LLM not available"
                print(f"📊 Running analysis without AI summary for project: {project_id} ({reason})")
                analytics_engine.run_analysis(project_id)
        
            print(f"✅ Analysis completed successfully for project: {project_id}")
        
            # Clean up the preference after analysis is complete
            _project_preferences.pop(project_id, None)
        
        except Exception as e:
            # Mark analysis as failed and log error
            print(f"❌ Analysis failed for project {project_id}: {str(e)}")
            # Clean up preference even on failure
            _project_preferences.pop(project_id, None)
            db.update_analysis_session_status(project_id, 'failed')
    
    @staticmethod
    def _estimate_analysis_duration(analysis_session) -> int:
        """
        Estimate analysis duration in minutes based on project parameters.
        
        Args:
            analysis_session: Analysis session object
            
        Returns:
            Estimated duration in minutes
        """
        try:
            keywords = json.loads(analysis_session.keywords)
            collection_ids = json.loads(analysis_session.collection_ids)
            
            # Base estimation: 1-2 minutes per keyword per collection
            base_time = len(keywords) * len(collection_ids) * 1.5
            
            # Add time for AI summary if available
            if is_llm_available():
                base_time += 2
            
            # Minimum 2 minutes, maximum 15 minutes for UI purposes
            return max(2, min(15, int(base_time)))
            
        except Exception:
            # Default estimate if calculation fails
            return 5
    
    @staticmethod
    def _get_analysis_progress(analysis_session) -> Dict[str, Any]:
        """
        Get progress information for running analysis.
        
        Args:
            analysis_session: Analysis session object
            
        Returns:
            Dictionary with progress information
        """
        # Calculate elapsed time
        elapsed_minutes = (datetime.utcnow().timestamp() - analysis_session.created_at) / 60
        estimated_duration = ProjectService._estimate_analysis_duration(analysis_session)
        
        # Calculate progress percentage (capped at 95% until actually complete)
        progress_percentage = min(95, int((elapsed_minutes / estimated_duration) * 100))
        
        return {
            "progress_percentage": progress_percentage,
            "estimated_completion_minutes": max(1, estimated_duration - int(elapsed_minutes)),
            "current_phase": ProjectService._determine_current_phase(progress_percentage),
            "elapsed_minutes": int(elapsed_minutes),
            "message": "Analysis is running. Please wait for completion."
        }
    
    @staticmethod
    def _determine_current_phase(progress_percentage: int) -> str:
        """Determine current analysis phase based on progress."""
        if progress_percentage < 20:
            return "Data Processing"
        elif progress_percentage < 40:
            return "Keyword Analysis"
        elif progress_percentage < 60:
            return "Sentiment Analysis" 
        elif progress_percentage < 80:
            return "Co-occurrence Analysis"
        else:
            return "AI Summary Generation" if is_llm_available() else "Finalizing Results"
    
    @staticmethod
    def _get_completion_info(analysis_session) -> Dict[str, Any]:
        """
        Get completion information for completed analysis.
        
        Args:
            analysis_session: Analysis session object
            
        Returns:
            Dictionary with completion information
        """
        return {
            "progress_percentage": 100,
            "completed_at": datetime.utcnow().isoformat(),
            "total_mentions": analysis_session.total_mentions or 0,
            "average_sentiment": analysis_session.avg_sentiment or 0.0,
            "has_ai_summary": analysis_summarizer.get_existing_summary(analysis_session.id) is not None,
            "message": "Analysis completed successfully. Results are available."
        }
    
    @staticmethod
    def _get_error_info(analysis_session) -> Dict[str, Any]:
        """
        Get error information for failed analysis.
        
        Args:
            analysis_session: Analysis session object
            
        Returns:
            Dictionary with error information
        """
        return {
            "progress_percentage": 0,
            "error": "Analysis failed to complete",
            "message": "Analysis encountered an error and was unable to complete. Please try running the analysis again.",
            "troubleshooting_tips": [
                "Verify that the selected collections contain valid data",
                "Check that keywords are properly formatted",
                "Ensure sufficient system resources are available",
                "Try running the analysis again after a few minutes"
            ]
        }
    
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
    async def _transform_session_to_project_with_results(session, session_results: Dict[str, Any]) -> ProjectResponse:
        """
        Transform an AnalysisSession with results into a ProjectResponse.
        
        Args:
            session: AnalysisSession object from database
            session_results: Complete session results from analytics engine
            
        Returns:
            ProjectResponse with enhanced results data
        """
        # Parse JSON fields from database
        keywords = json.loads(session.keywords)
        collection_ids = json.loads(session.collection_ids)
        
        # Create enhanced stats object with results data
        stats = ProjectService._calculate_enhanced_project_stats(session, session_results, keywords, collection_ids)
        
        # Get AI summary if it exists
        summary = await ProjectService._get_project_summary(session.id)
        
        # Get collections metadata
        collections_metadata = ProjectService._get_collections_metadata(collection_ids)
        
        # Convert created_at timestamp to datetime
        created_at = datetime.fromtimestamp(session.created_at)
        
        return ProjectResponse(
            id=session.id,
            name=session.name,
            research_question=None,
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
        """Calculate basic project statistics from session data."""
        return ProjectStats(
            total_mentions=session.total_mentions or 0,
            avg_sentiment=session.avg_sentiment or 0.0,
            keywords_count=len(keywords),
            collections_count=len(collection_ids),
            posts_analyzed=0,  # Will be enhanced in results version
            comments_analyzed=0  # Will be enhanced in results version
        )
    
    @staticmethod
    def _calculate_enhanced_project_stats(session, session_results: Dict[str, Any], 
                                        keywords: List[str], collection_ids: List[str]) -> ProjectStats:
        """Calculate enhanced project statistics with results data."""
        # Count actual posts and comments analyzed
        keywords_data = session_results.get('keywords_data', [])
        total_posts = sum(kw.get('posts_found_in', 0) for kw in keywords_data)
        total_comments = sum(kw.get('comments_found_in', 0) for kw in keywords_data)
        
        return ProjectStats(
            total_mentions=session.total_mentions or 0,
            avg_sentiment=session.avg_sentiment or 0.0,
            keywords_count=len(keywords),
            collections_count=len(collection_ids),
            posts_analyzed=total_posts,
            comments_analyzed=total_comments
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
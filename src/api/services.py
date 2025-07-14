"""
API Service Layer

Business logic and data transformation functions for API endpoints.
Handles the complex work of converting between backend data structures
and frontend-friendly API responses.

Enhanced with Step 3: Analysis Workflow Management
Enhanced with Step 4: Chat and AI Feature Services
Enhanced with Step 5: Collection Management Services
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import BackgroundTasks
import json
import uuid
import asyncio

from src.analytics import analytics_engine
from src.database import db
from src.llm.services.summarizer import analysis_summarizer
from src.llm import is_llm_available, get_llm_provider
from src.collector import collector, CollectionParameters
from .models import (
    ProjectResponse, ProjectStats, ProjectSummary, ProjectCreate,
    ChatResponse, ChatMessage, ChatSessionInfo, ChatSessionListResponse, 
    ChatHistoryResponse, ChatMessageCreate, KeywordSuggestionRequest,
    KeywordSuggestionResponse, AIStatusResponse, CollectionCreateRequest,
    CollectionResponse, CollectionBatchResponse, CollectionBatchStatusResponse,
    CollectionListResponse
)

# Temporary in-memory storage for project preferences
_project_preferences = {}

# Temporary in-memory storage for collection batch tracking
_collection_batches = {}


class ProjectService:
    """Service class for project-related operations with analysis workflow and chat/AI management."""
    
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
    # ANALYSIS WORKFLOW METHODS (STEP 3)
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
            print(f"Unexpected error in start_analysis endpoint: {e}")
            raise ValueError(f"Failed to start analysis: {str(e)}")
    
    @staticmethod
    async def get_analysis_status(project_id: str) -> Dict[str, Any]:
        """Get current analysis status and progress for a project."""
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
        """Get complete analysis results for a project."""
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
    # CHAT AND AI FEATURE METHODS (EXISTING - STEP 4)
    # ============================================================================
    
    @staticmethod
    async def get_chat_sessions(project_id: str) -> ChatSessionListResponse:
        """
        Get all chat sessions for a project.
        
        Args:
            project_id: Project ID to get chat sessions for
            
        Returns:
            ChatSessionListResponse with session information
        """
        try:
            # Validate project exists
            analysis_session = db.get_analysis_session(project_id)
            if not analysis_session:
                raise ValueError(f"Project not found: {project_id}")
            
            # Import chat agent
            from src.llm.services.chat_agent import chat_agent
            
            # Get chat sessions from backend
            session_summaries = chat_agent.list_chat_sessions(project_id)
            
            # Transform to API model format
            sessions = []
            for summary in session_summaries:
                session_info = ChatSessionInfo(
                    session_id=summary['session_id'],
                    created_at=datetime.fromtimestamp(summary['created_at']),
                    last_active=datetime.fromtimestamp(summary['last_active']),
                    message_count=summary['message_count'],
                    preview=summary['preview']
                )
                sessions.append(session_info)
            
            return ChatSessionListResponse(
                sessions=sessions,
                total_count=len(sessions)
            )
            
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Error in get_chat_sessions: {e}")
            raise ValueError(f"Failed to get chat sessions: {str(e)}")
    
    @staticmethod
    async def start_chat_session(project_id: str) -> ChatSessionInfo:
        """
        Start a new chat session for a project.
        
        Args:
            project_id: Project ID to start chat for
            
        Returns:
            ChatSessionInfo for the new session
        """
        try:
            # Validate project exists and is completed
            analysis_session = db.get_analysis_session(project_id)
            if not analysis_session:
                raise ValueError(f"Project not found: {project_id}")
            
            if analysis_session.status != 'completed':
                raise ValueError(f"Project analysis not completed. Current status: {analysis_session.status}")
            
            # Check if LLM is available
            if not is_llm_available():
                raise ValueError("AI chat features are not available. Please check LLM configuration.")
            
            # Import chat agent
            from src.llm.services.chat_agent import chat_agent
            
            # Start new chat session
            chat_session_id = chat_agent.start_chat_session(project_id)
            
            # Return session info
            return ChatSessionInfo(
                session_id=chat_session_id,
                created_at=datetime.utcnow(),
                last_active=datetime.utcnow(),
                message_count=1,  # Welcome message
                preview="New chat session started"
            )
            
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Error in start_chat_session: {e}")
            raise ValueError(f"Failed to start chat session: {str(e)}")
    
    @staticmethod
    async def send_chat_message(chat_session_id: str, message_data: ChatMessageCreate) -> ChatResponse:
        """
        Send a message to a chat session.
        
        Args:
            chat_session_id: Chat session ID
            message_data: Message to send
            
        Returns:
            ChatResponse with AI response
        """
        try:
            # Check if LLM is available
            if not is_llm_available():
                raise ValueError("AI chat features are not available. Please check LLM configuration.")
            
            # Import chat agent
            from src.llm.services.chat_agent import chat_agent
            
            # Send message to chat agent
            response = chat_agent.send_message(
                chat_session_id=chat_session_id,
                user_message=message_data.message,
                search_type=message_data.search_type
            )
            
            # Transform to API model format
            return ChatResponse(
                message=response.message,
                sources=response.sources,
                analytics_insights=response.analytics_insights,
                search_type=response.search_type,
                discussions_found=response.discussions_found,
                tokens_used=response.tokens_used,
                cost_estimate=response.cost_estimate,
                session_id=response.session_id,
                query_classification=response.query_classification
            )
            
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Error in send_chat_message: {e}")
            raise ValueError(f"Failed to send chat message: {str(e)}")
    
    @staticmethod
    async def get_chat_history(chat_session_id: str, limit: int = 50) -> ChatHistoryResponse:
        """
        Get chat history for a session.
        
        Args:
            chat_session_id: Chat session ID
            limit: Maximum number of messages to return
            
        Returns:
            ChatHistoryResponse with messages
        """
        try:
            # Import chat agent
            from src.llm.services.chat_agent import chat_agent
            
            # Get chat history from backend
            history = chat_agent.get_chat_history(chat_session_id, limit)
            
            # Transform to API model format
            messages = []
            for msg in history:
                chat_message = ChatMessage(
                    id=msg.get('id', 0),  # Backend should provide ID
                    role=msg['role'],
                    content=msg['content'],
                    timestamp=datetime.fromtimestamp(msg['timestamp']),
                    tokens_used=msg.get('tokens_used', 0),
                    cost_estimate=msg.get('cost_estimate', 0.0)
                )
                messages.append(chat_message)
            
            return ChatHistoryResponse(
                messages=messages,
                session_id=chat_session_id,
                total_messages=len(messages)
            )
            
        except Exception as e:
            print(f"Error in get_chat_history: {e}")
            raise ValueError(f"Failed to get chat history: {str(e)}")
    
    @staticmethod
    async def suggest_keywords(suggestion_request: KeywordSuggestionRequest) -> KeywordSuggestionResponse:
        """
        Get AI keyword suggestions for research.
        
        Args:
            suggestion_request: Request with research description
            
        Returns:
            KeywordSuggestionResponse with suggested keywords
        """
        try:
            # Check if LLM is available
            if not is_llm_available():
                raise ValueError("AI keyword suggestion features are not available. Please check LLM configuration.")
            
            # Get LLM provider
            provider = get_llm_provider()
            if not provider:
                raise ValueError("No LLM provider available for keyword suggestions.")
            
            # Create keyword suggestion prompt
            system_prompt = """You are a helpful assistant that suggests relevant keywords for analyzing Reddit discussions. 
Given a research goal or topic, suggest 5-10 specific keywords that would be effective for finding relevant posts and comments.

Guidelines:
- Suggest ONLY single words, not phrases (e.g. "battery" not "battery life")
- Include related terms and synonyms as separate single words
- Consider common abbreviations and slang terms
- Think about how people actually discuss this topic on Reddit
- Include words that capture both positive and negative aspects
- Each keyword should be one word that is specific enough to be meaningful

Return only the keywords, separated by commas, with no additional explanation."""
            
            user_prompt = f"Research goal: {suggestion_request.research_description}\n\nSuggest relevant keywords for Reddit analysis:"
            
            # Generate keywords
            response = provider.generate(user_prompt, system_prompt)
            
            if not response.content:
                raise ValueError("No keywords were generated. Please try rephrasing your research description.")
            
            # Parse keywords from response
            keywords = [kw.strip().strip('"\'') for kw in response.content.split(',')]
            keywords = [kw for kw in keywords if kw]  # Remove empty strings
            keywords = keywords[:suggestion_request.max_keywords]  # Limit to requested number
            
            return KeywordSuggestionResponse(
                keywords=keywords,
                research_description=suggestion_request.research_description,
                provider=response.provider,
                model=response.model,
                tokens_used=response.tokens_used,
                cost_estimate=response.cost_estimate
            )
            
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Error in suggest_keywords: {e}")
            raise ValueError(f"Failed to generate keyword suggestions: {str(e)}")
    
    @staticmethod
    async def get_ai_status() -> AIStatusResponse:
        """
        Get current AI system status and capabilities.
        
        Returns:
            AIStatusResponse with system status
        """
        try:
            # Check overall LLM availability
            ai_available = is_llm_available()
            
            # Get provider information
            providers = {}
            features = {
                "keyword_suggestion": False,
                "summarization": False,
                "chat_agent": False,
                "rag_search": False
            }
            default_provider = None
            embeddings_info = {}
            
            if ai_available:
                try:
                    from src.llm.config import llm_config
                    
                    # Get available providers
                    available_providers = llm_config.get_available_providers()
                    default_provider = llm_config.get_default_provider()
                    
                    # Test each provider
                    test_results = llm_config.test_providers()
                    
                    for provider_name in available_providers:
                        config = llm_config.get_provider_config(provider_name)
                        test_success, test_message = test_results.get(provider_name, (False, "Not tested"))
                        
                        providers[provider_name] = {
                            "available": test_success,
                            "model": config.get('model', 'unknown') if config else 'unknown',
                            "status": test_message
                        }
                    
                    # Get feature availability
                    features = llm_config.get_feature_config()
                    
                    # Get embeddings info
                    embeddings_config = llm_config.get_embeddings_config()
                    if embeddings_config:
                        embeddings_info = {
                            "provider": embeddings_config.get('provider', 'unknown'),
                            "model": embeddings_config.get('model', 'unknown'),
                            "available": True
                        }
                    
                except Exception as e:
                    print(f"Error getting detailed AI status: {e}")
                    # Fallback to basic status
                    providers = {"unknown": {"available": ai_available, "status": "Basic availability check only"}}
            
            return AIStatusResponse(
                ai_available=ai_available,
                providers=providers,
                features=features,
                default_provider=default_provider,
                embeddings_info=embeddings_info
            )
            
        except Exception as e:
            print(f"Error in get_ai_status: {e}")
            # Return basic unavailable status rather than failing
            return AIStatusResponse(
                ai_available=False,
                providers={},
                features={"keyword_suggestion": False, "summarization": False, "chat_agent": False, "rag_search": False},
                default_provider=None,
                embeddings_info={}
            )
    
    # ============================================================================
    # PRIVATE HELPER METHODS (EXISTING + ENHANCEMENTS)
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
        """Estimate analysis duration in minutes based on project parameters."""
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
        """Get progress information for running analysis."""
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
        """Get completion information for completed analysis."""
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
        """Get error information for failed analysis."""
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
        """Transform an AnalysisSession into a ProjectResponse."""
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
        """Transform an AnalysisSession with results into a ProjectResponse."""
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
        """Get AI summary for a project if it exists."""
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
        """Get metadata about collections for frontend display."""
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
        """Validate that all specified collection IDs exist."""
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


# ============================================================================
# COLLECTION SERVICE (NEW - STEP 5)
# ============================================================================

class CollectionService:
    """Service class for collection management operations."""
    
    @staticmethod
    async def create_collections(request: CollectionCreateRequest, background_tasks: BackgroundTasks) -> CollectionBatchResponse:
        """
        Create collections for multiple subreddits.
        
        Args:
            request: Collection creation request with subreddits and parameters
            background_tasks: FastAPI background tasks for async processing
            
        Returns:
            CollectionBatchResponse with batch tracking information
        """
        try:
            # Generate unique batch ID for tracking
            batch_id = str(uuid.uuid4())
            
            # Create collection records for each subreddit
            collection_ids = []
            for subreddit in request.subreddits:
                collection_id = db.create_collection(
                    subreddit=subreddit,
                    sort_method=request.collection_params.sort_method,
                    time_period=request.collection_params.time_period,
                    posts_requested=request.collection_params.posts_count,
                    root_comments_requested=request.collection_params.root_comments,
                    replies_per_root=request.collection_params.replies_per_root,
                    min_upvotes=request.collection_params.min_upvotes
                )
                collection_ids.append(collection_id)
            
            # Initialize batch tracking
            _collection_batches[batch_id] = {
                'subreddits': request.subreddits,
                'collection_ids': collection_ids,
                'collection_params': request.collection_params,
                'status': 'started',
                'started_at': datetime.utcnow(),
                'current_index': 0,
                'completed_subreddits': [],
                'failed_subreddits': [],
                'error_messages': {}
            }
            
            # Start background collection task
            background_tasks.add_task(
                CollectionService._run_background_collection,
                batch_id,
                request.subreddits,
                collection_ids,
                request.collection_params
            )
            
            # Estimate duration based on number of subreddits and posts
            estimated_duration = CollectionService._estimate_collection_duration(
                len(request.subreddits), 
                request.collection_params.posts_count
            )
            
            return CollectionBatchResponse(
                batch_id=batch_id,
                collection_ids=collection_ids,
                subreddits=request.subreddits,
                status='started',
                started_at=datetime.utcnow(),
                estimated_duration_minutes=estimated_duration
            )
            
        except Exception as e:
            print(f"Error in CollectionService.create_collections: {e}")
            raise ValueError(f"Failed to create collections: {str(e)}")
    
    @staticmethod
    async def get_batch_status(batch_id: str) -> CollectionBatchStatusResponse:
        """
        Get status of a collection batch.
        
        Args:
            batch_id: Batch ID to check status for
            
        Returns:
            CollectionBatchStatusResponse with current status
        """
        try:
            # Check if batch exists
            if batch_id not in _collection_batches:
                raise ValueError(f"Collection batch not found: {batch_id}")
            
            batch_info = _collection_batches[batch_id]
            
            # Get current collection statuses from database
            collections = []
            for collection_id in batch_info['collection_ids']:
                collection_data = CollectionService._get_collection_response(collection_id)
                if collection_data:
                    collections.append(collection_data)
            
            # Calculate overall progress
            completed_count = len(batch_info['completed_subreddits'])
            failed_count = len(batch_info['failed_subreddits'])
            total_count = len(batch_info['subreddits'])
            
            if completed_count + failed_count >= total_count:
                overall_status = 'completed'
                progress_percentage = 100
                current_subreddit = None
            elif batch_info['status'] == 'running':
                overall_status = 'running'
                progress_percentage = int((completed_count + failed_count) / total_count * 100)
                current_index = batch_info['current_index']
                current_subreddit = batch_info['subreddits'][current_index] if current_index < len(batch_info['subreddits']) else None
            else:
                overall_status = batch_info['status']
                progress_percentage = 0
                current_subreddit = None
            
            # Calculate estimated completion
            estimated_completion = None
            if overall_status == 'running' and progress_percentage > 0:
                elapsed_minutes = (datetime.utcnow() - batch_info['started_at']).total_seconds() / 60
                estimated_total_minutes = elapsed_minutes / (progress_percentage / 100)
                estimated_completion = batch_info['started_at'] + timedelta(minutes=estimated_total_minutes)
            
            return CollectionBatchStatusResponse(
                batch_id=batch_id,
                status=overall_status,
                progress_percentage=progress_percentage,
                current_subreddit=current_subreddit,
                completed_subreddits=batch_info['completed_subreddits'],
                failed_subreddits=batch_info['failed_subreddits'],
                collections=collections,
                started_at=batch_info['started_at'],
                estimated_completion=estimated_completion
            )
            
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Error in CollectionService.get_batch_status: {e}")
            raise ValueError(f"Failed to get batch status: {str(e)}")
    
    @staticmethod
    async def get_all_collections() -> CollectionListResponse:
        """
        Get all collections with metadata.
        
        Returns:
            CollectionListResponse with all collections
        """
        try:
            # Get all collections from database
            db_collections = db.get_collections()
            
            # Transform to API response format
            collections = []
            for db_collection in db_collections:
                collection_response = CollectionService._get_collection_response(db_collection.id)
                if collection_response:
                    collections.append(collection_response)
            
            return CollectionListResponse(
                collections=collections,
                total_count=len(collections)
            )
            
        except Exception as e:
            print(f"Error in CollectionService.get_all_collections: {e}")
            raise ValueError(f"Failed to get collections: {str(e)}")
    
    @staticmethod
    async def delete_collection(collection_id: str) -> bool:
        """
        Delete a specific collection.
        
        Args:
            collection_id: Collection ID to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        try:
            # Get collection from database to check if it exists
            session = db.get_session()
            try:
                from src.database import Collection
                collection = session.query(Collection).filter(Collection.id == collection_id).first()
                
                if not collection:
                    return False
                
                # Delete the collection (cascade will handle posts and comments)
                session.delete(collection)
                session.commit()
                
                return True
                
            finally:
                session.close()
                
        except Exception as e:
            print(f"Error in CollectionService.delete_collection: {e}")
            raise ValueError(f"Failed to delete collection: {str(e)}")
    
    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================
    
    @staticmethod
    async def _run_background_collection(batch_id: str, subreddits: List[str], 
                                        collection_ids: List[str], collection_params):
        """Run collection in background task."""
        try:
            print(f"🚀 Starting background collection for batch: {batch_id}")
            
            # Update batch status to running
            if batch_id in _collection_batches:
                _collection_batches[batch_id]['status'] = 'running'
            
            # Process each subreddit
            for i, subreddit in enumerate(subreddits):
                try:
                    print(f"📊 Collecting from r/{subreddit} ({i+1}/{len(subreddits)})")
                    
                    # Update current processing index
                    if batch_id in _collection_batches:
                        _collection_batches[batch_id]['current_index'] = i
                    
                    # Create collection parameters
                    params = CollectionParameters(
                        subreddit=subreddit,
                        sort_method=collection_params.sort_method,
                        time_period=collection_params.time_period,
                        posts_count=collection_params.posts_count,
                        root_comments=collection_params.root_comments,
                        replies_per_root=collection_params.replies_per_root,
                        min_upvotes=collection_params.min_upvotes
                    )
                    
                    # Run collection using existing collector
                    collection_id = collection_ids[i]
                    collector.current_collection_id = collection_id
                    collector.collect_data(params)
                    
                    # Mark as completed
                    if batch_id in _collection_batches:
                        _collection_batches[batch_id]['completed_subreddits'].append(subreddit)
                    
                    print(f"✅ Completed r/{subreddit}")
                    
                except Exception as e:
                    print(f"❌ Failed to collect r/{subreddit}: {str(e)}")
                    
                    # Mark collection as failed in database
                    db.update_collection_status(collection_ids[i], 'failed')
                    
                    # Track failure in batch
                    if batch_id in _collection_batches:
                        _collection_batches[batch_id]['failed_subreddits'].append(subreddit)
                        _collection_batches[batch_id]['error_messages'][subreddit] = str(e)
            
            # Update final batch status
            if batch_id in _collection_batches:
                _collection_batches[batch_id]['status'] = 'completed'
            
            print(f"✅ Collection batch completed: {batch_id}")
            
            # Clean up batch tracking after a delay (keep for a while for status checking)
            await asyncio.sleep(300)  # Keep for 5 minutes
            _collection_batches.pop(batch_id, None)
            
        except Exception as e:
            print(f"❌ Collection batch failed {batch_id}: {str(e)}")
            
            # Mark batch as failed
            if batch_id in _collection_batches:
                _collection_batches[batch_id]['status'] = 'failed'
    
    @staticmethod
    def _estimate_collection_duration(subreddit_count: int, posts_per_subreddit: int) -> int:
        """Estimate collection duration in minutes."""
        # Base estimation: ~0.5 minutes per subreddit for basic collection
        # Add more time for larger post counts
        base_time = subreddit_count * 0.5
        
        # Add time based on posts (more posts = more comments to collect)
        if posts_per_subreddit > 50:
            base_time += subreddit_count * 2  # Extra time for large collections
        elif posts_per_subreddit > 20:
            base_time += subreddit_count * 1  # Moderate extra time
        
        # Minimum 1 minute, maximum 30 minutes for UI purposes
        return max(1, min(30, int(base_time)))
    
    @staticmethod
    def _get_collection_response(collection_id: str) -> Optional[CollectionResponse]:
        """Transform a database collection into a CollectionResponse."""
        try:
            session = db.get_session()
            try:
                from src.database import Collection, Post, Comment
                
                # Get collection from database
                collection = session.query(Collection).filter(Collection.id == collection_id).first()
                if not collection:
                    return None
                
                # Count actual posts and comments collected
                posts_collected = session.query(Post).filter(Post.collection_id == collection_id).count()
                comments_collected = session.query(Comment).filter(Comment.collection_id == collection_id).count()
                
                return CollectionResponse(
                    id=collection.id,
                    subreddit=collection.subreddit,
                    sort_method=collection.sort_method,
                    time_period=collection.time_period,
                    posts_requested=collection.posts_requested,
                    posts_collected=posts_collected,
                    comments_collected=comments_collected,
                    status=collection.status,
                    created_at=datetime.fromtimestamp(collection.created_at),
                    error_message=None  # Could be enhanced to store error messages
                )
                
            finally:
                session.close()
                
        except Exception as e:
            print(f"Error transforming collection {collection_id}: {e}")
            return None
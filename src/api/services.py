"""
API Service Layer

Business logic and data transformation functions for API endpoints.
Handles the complex work of converting between backend data structures
and frontend-friendly API responses.

Enhanced with Step 3: Analysis Workflow Management
Enhanced with Step 4: Chat and AI Feature Services
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import BackgroundTasks
import json

from src.analytics import analytics_engine
from src.database import db
from src.llm.services.summarizer import analysis_summarizer
from src.llm import is_llm_available, get_llm_provider
from .models import (
    ProjectResponse, ProjectStats, ProjectSummary, ProjectCreate,
    ChatResponse, ChatMessage, ChatSessionInfo, ChatSessionListResponse, 
    ChatHistoryResponse, ChatMessageCreate, KeywordSuggestionRequest,
    KeywordSuggestionResponse, AIStatusResponse, AIExplanationRequest,
    AIExplanationResponse
)

# Temporary in-memory storage for project preferences
_project_preferences = {}


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
    # CHAT AND AI FEATURE METHODS (NEW - STEP 4)
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
    
    @staticmethod
    async def explain_analysis(project_id: str, explanation_request: AIExplanationRequest) -> AIExplanationResponse:
        """
        Get AI explanation of analysis results for a specific topic.
        
        Args:
            project_id: Project ID to explain
            explanation_request: Request with topic to explain
            
        Returns:
            AIExplanationResponse with explanation
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
                raise ValueError("AI explanation features are not available. Please check LLM configuration.")
            
            # Get analysis results
            session_results = analytics_engine.get_session_results_with_summary(project_id)
            collection_ids = json.loads(analysis_session.collection_ids)
            
            # Get LLM provider
            provider = get_llm_provider()
            if not provider:
                raise ValueError("No LLM provider available for explanations.")
            
            # Build context for explanation
            context_parts = [
                f"Analysis Overview:",
                f"- Total mentions: {session_results.get('total_mentions', 0)}",
                f"- Average sentiment: {session_results.get('avg_sentiment', 0.0):.3f}",
                f"- Keywords analyzed: {len(session_results.get('keywords', []))}"
            ]
            
            # Add relevant keyword data
            keywords_data = session_results.get('keywords_data', [])
            if keywords_data:
                context_parts.append("\nTop Keywords:")
                for kw in keywords_data[:5]:
                    context_parts.append(f"- '{kw['keyword']}': {kw['total_mentions']} mentions, {kw['avg_sentiment']:+.3f} sentiment")
            
            context = "\n".join(context_parts)
            
            # Create explanation prompt
            system_prompt = """You are an expert data analyst who explains Reddit discussion analytics in clear, business-relevant terms. 
Your explanations should help users understand what the data means for their research goals and what actions they might take based on the insights."""
            
            user_prompt = f"""Based on this Reddit discussion analysis, please explain the following topic: "{explanation_request.topic}"

Analysis Data:
{context}

Additional Context: {explanation_request.context or "None provided"}

Please provide a clear explanation that:
1. Explains what the data shows about this topic
2. Interprets the business/research implications
3. Suggests what this means for the user's research
4. Identifies any notable patterns or insights related to this topic

Focus on practical, actionable insights rather than just restating the numbers."""
            
            # Generate explanation
            response = provider.generate(user_prompt, system_prompt)
            
            if not response.content:
                raise ValueError("No explanation was generated. Please try rephrasing your request.")
            
            # Generate related insights
            related_insights = []
            if keywords_data:
                # Find keywords related to the topic
                topic_lower = explanation_request.topic.lower()
                related_keywords = [
                    kw for kw in keywords_data 
                    if topic_lower in kw['keyword'].lower() or kw['keyword'].lower() in topic_lower
                ]
                
                if related_keywords:
                    related_insights.append(f"Found {len(related_keywords)} keywords directly related to '{explanation_request.topic}'")
                
                # Find sentiment patterns
                positive_kw = [kw for kw in keywords_data if kw['avg_sentiment'] > 0.1]
                negative_kw = [kw for kw in keywords_data if kw['avg_sentiment'] < -0.1]
                
                if len(negative_kw) > len(positive_kw):
                    related_insights.append("Overall discussion sentiment trends negative")
                elif len(positive_kw) > len(negative_kw):
                    related_insights.append("Overall discussion sentiment trends positive")
            
            # Prepare sources used
            sources_used = [
                {
                    "type": "analysis_overview",
                    "total_mentions": session_results.get('total_mentions', 0),
                    "avg_sentiment": session_results.get('avg_sentiment', 0.0),
                    "keywords_count": len(session_results.get('keywords', []))
                }
            ]
            
            return AIExplanationResponse(
                explanation=response.content,
                topic=explanation_request.topic,
                related_insights=related_insights,
                sources_used=sources_used,
                provider=response.provider,
                model=response.model,
                tokens_used=response.tokens_used,
                cost_estimate=response.cost_estimate
            )
            
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Error in explain_analysis: {e}")
            raise ValueError(f"Failed to generate explanation: {str(e)}")
    
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
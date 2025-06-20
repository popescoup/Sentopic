"""
Chat Agent Service

Manages conversational AI interactions with analysis data.
Handles chat sessions, conversation context, and integration with RAG engine.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from ...database import db, ChatSession, ChatMessage
from .rag_engine import rag_engine


@dataclass
class ChatResponse:
    """Response from chat agent."""
    message: str                   # Assistant's response
    sources: List[Dict[str, Any]]  # Source attributions (if any)
    search_type: str              # Search method used (if any)
    tokens_used: int              # Tokens used for this response
    cost_estimate: float          # Cost estimate for this response
    session_id: str               # Chat session ID


class ChatAgent:
    """
    Chat agent for conversational analysis exploration.
    
    Manages chat sessions, maintains conversation context,
    and provides intelligent responses using RAG.
    """
    
    def __init__(self):
        self.max_context_messages = 10  # 5 user + 5 assistant pairs
    
    def start_chat_session(self, analysis_session_id: str) -> str:
        """
        Start a new chat session for an analysis session.
        
        Args:
            analysis_session_id: Analysis session to chat about
        
        Returns:
            Chat session ID
        """
        # Validate analysis session exists
        analysis_session = db.get_analysis_session(analysis_session_id)
        if not analysis_session:
            raise ValueError(f"Analysis session not found: {analysis_session_id}")
        
        if analysis_session.status != 'completed':
            raise ValueError(f"Analysis session not completed: {analysis_session.status}")
        
        # Create chat session
        chat_session_id = db.create_chat_session(analysis_session_id)
        
        # Send welcome message
        welcome_message = self._create_welcome_message(analysis_session)
        
        db.save_chat_message(
            chat_session_id=chat_session_id,
            role='assistant',
            content=welcome_message
        )
        
        return chat_session_id
    
    def send_message(self, chat_session_id: str, user_message: str, 
                    search_type: str = 'keyword') -> ChatResponse:
        """
        Send a message and get response from chat agent.
        
        Args:
            chat_session_id: Chat session ID
            user_message: User's message
            search_type: Search method to use
        
        Returns:
            ChatResponse with assistant's reply
        """
        # Validate chat session
        chat_session = self._get_chat_session(chat_session_id)
        if not chat_session:
            raise ValueError(f"Chat session not found: {chat_session_id}")
        
        # Get analysis session info
        analysis_session = db.get_analysis_session(chat_session.analysis_session_id)
        collection_ids = json.loads(analysis_session.collection_ids)
        
        # Save user message
        db.save_chat_message(
            chat_session_id=chat_session_id,
            role='user',
            content=user_message
        )
        
        # Check for special commands
        special_response = self._handle_special_commands(user_message, chat_session_id, analysis_session)
        if special_response:
            # Save assistant response
            db.save_chat_message(
                chat_session_id=chat_session_id,
                role='assistant',
                content=special_response['message'],
                tokens_used=special_response.get('tokens_used', 0),
                cost_estimate=special_response.get('cost_estimate', 0.0)
            )
            
            return ChatResponse(
                message=special_response['message'],
                sources=special_response.get('sources', []),
                search_type='command',
                tokens_used=special_response.get('tokens_used', 0),
                cost_estimate=special_response.get('cost_estimate', 0.0),
                session_id=chat_session_id
            )
        
        # Use RAG to answer the question
        try:
            rag_response = rag_engine.answer_question(
                question=user_message,
                collection_ids=collection_ids,
                search_type=search_type,
                max_results=5
            )
            
            # Save assistant response
            db.save_chat_message(
                chat_session_id=chat_session_id,
                role='assistant',
                content=rag_response.answer,
                tokens_used=rag_response.tokens_used,
                cost_estimate=rag_response.cost_estimate
            )
            
            return ChatResponse(
                message=rag_response.answer,
                sources=rag_response.sources,
                search_type=rag_response.search_type,
                tokens_used=rag_response.tokens_used,
                cost_estimate=rag_response.cost_estimate,
                session_id=chat_session_id
            )
            
        except Exception as e:
            error_message = f"I encountered an error while processing your question: {str(e)}"
            
            # Save error response
            db.save_chat_message(
                chat_session_id=chat_session_id,
                role='assistant',
                content=error_message
            )
            
            return ChatResponse(
                message=error_message,
                sources=[],
                search_type=search_type,
                tokens_used=0,
                cost_estimate=0.0,
                session_id=chat_session_id
            )
    
    def get_chat_history(self, chat_session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get chat history for a session.
        
        Args:
            chat_session_id: Chat session ID
            limit: Maximum messages to return
        
        Returns:
            List of messages in chronological order
        """
        messages = db.get_chat_messages(chat_session_id, limit)
        
        # Convert to chronological order and format
        formatted_messages = []
        for message in reversed(messages):  # Reverse since DB returns newest first
            formatted_messages.append({
                'role': message.role,
                'content': message.content,
                'timestamp': message.timestamp,
                'tokens_used': message.tokens_used,
                'cost_estimate': message.cost_estimate
            })
        
        return formatted_messages
    
    def get_available_search_types(self, chat_session_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get available search types for this chat session.
        
        Args:
            chat_session_id: Chat session ID
        
        Returns:
            Dictionary with search type availability
        """
        # Get chat session and analysis session
        chat_session = self._get_chat_session(chat_session_id)
        if not chat_session:
            raise ValueError(f"Chat session not found: {chat_session_id}")
        
        analysis_session = db.get_analysis_session(chat_session.analysis_session_id)
        collection_ids = json.loads(analysis_session.collection_ids)
        
        return rag_engine.get_available_search_types(collection_ids)
    
    def get_full_context(self, chat_session_id: str, content_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full context for a specific content ID mentioned in chat.
        
        Args:
            chat_session_id: Chat session ID
            content_id: Content ID to get full context for
        
        Returns:
            Full content details or None if not found
        """
        # Get chat session and analysis session
        chat_session = self._get_chat_session(chat_session_id)
        if not chat_session:
            return None
        
        analysis_session = db.get_analysis_session(chat_session.analysis_session_id)
        collection_ids = json.loads(analysis_session.collection_ids)
        
        # Try to find the content in any of the collections
        for collection_id in collection_ids:
            # Try as post first
            context = rag_engine.get_full_context(content_id, 'post', collection_id)
            if context:
                return context
            
            # Try as comment
            context = rag_engine.get_full_context(content_id, 'comment', collection_id)
            if context:
                return context
        
        return None
    
    def list_chat_sessions(self, analysis_session_id: str) -> List[Dict[str, Any]]:
        """
        List all chat sessions for an analysis session.
        
        Args:
            analysis_session_id: Analysis session ID
        
        Returns:
            List of chat session summaries
        """
        chat_sessions = db.get_chat_sessions(analysis_session_id)
        
        session_summaries = []
        for session in chat_sessions:
            # Get first few messages to create a preview
            messages = db.get_chat_messages(session.id, limit=3)
            
            # Create preview from first user message
            preview = "New chat session"
            for message in reversed(messages):
                if message.role == 'user':
                    preview = message.content[:100] + "..." if len(message.content) > 100 else message.content
                    break
            
            session_summaries.append({
                'session_id': session.id,
                'created_at': session.created_at,
                'last_active': session.last_active,
                'preview': preview,
                'message_count': len(messages)
            })
        
        return session_summaries
    
    def _get_chat_session(self, chat_session_id: str) -> Optional[ChatSession]:
        """Get chat session from database."""
        session = db.get_session()
        try:
            return session.query(ChatSession).filter(ChatSession.id == chat_session_id).first()
        finally:
            session.close()
    
    def _create_welcome_message(self, analysis_session) -> str:
        """Create welcome message for new chat session."""
        keywords = json.loads(analysis_session.keywords)
        keywords_text = ", ".join(keywords[:5])
        if len(keywords) > 5:
            keywords_text += f" (and {len(keywords) - 5} more)"
        
        return f"""👋 Welcome to your analysis chat session!

**Analysis:** {analysis_session.name}
**Keywords:** {keywords_text}
**Total Mentions:** {analysis_session.total_mentions:,}
**Avg Sentiment:** {analysis_session.avg_sentiment:+.3f}

I can help you explore your Reddit discussion data. You can ask me questions like:
• "What are the main complaints about [topic]?"
• "Show me positive comments about [keyword]"
• "What trends do you see in the data?"
• "Find posts with high engagement about [topic]"

**Search Modes Available:**
• **Keyword** (free, instant) - Good for exact matches
• **Semantic** (may require indexing) - Better for conceptual questions

Type your first question to get started! 🚀"""
    
    def _handle_special_commands(self, message: str, chat_session_id: str, 
                                analysis_session) -> Optional[Dict[str, Any]]:
        """Handle special commands like showing full context."""
        message_lower = message.lower().strip()
        
        # Handle context requests like "show full context for abc123"
        if message_lower.startswith(('show full context for', 'full context for', 'show context for')):
            # Extract content ID
            content_id = message.split()[-1]
            
            context = self.get_full_context(chat_session_id, content_id)
            if context:
                response = self._format_full_context(context)
                return {
                    'message': response,
                    'sources': [context],
                    'tokens_used': 0,
                    'cost_estimate': 0.0
                }
            else:
                return {
                    'message': f"I couldn't find content with ID '{content_id}' in your analysis data.",
                    'sources': [],
                    'tokens_used': 0,
                    'cost_estimate': 0.0
                }
        
        # Handle help requests
        if message_lower in ['help', '/help', 'commands', 'what can you do']:
            return {
                'message': self._get_help_message(),
                'sources': [],
                'tokens_used': 0,
                'cost_estimate': 0.0
            }
        
        return None
    
    def _format_full_context(self, context: Dict[str, Any]) -> str:
        """Format full context for display."""
        content_type = context['content_type'].title()
        author = context.get('author', 'Unknown')
        score = context.get('score', 0)
        created_date = datetime.fromtimestamp(context['created_utc']).strftime('%Y-%m-%d %H:%M')
        
        response = f"""**{content_type} ID: {context['content_id']}**
**Author:** {author} | **Score:** {score} | **Date:** {created_date}

"""
        
        if context['content_type'] == 'post':
            response += f"**Title:** {context.get('title', 'No title')}\n\n"
            if context.get('url'):
                response += f"**URL:** {context['url']}\n\n"
            response += f"**Content:**\n{context.get('content', 'No content')}"
        else:  # comment
            response += f"**Comment Content:**\n{context['content']}"
            if context.get('is_root'):
                response += "\n\n*(This is a root comment - direct reply to the post)*"
            else:
                response += f"\n\n*(Reply to comment, depth: {context.get('depth', 'unknown')})*"
        
        return response
    
    def _get_help_message(self) -> str:
        """Get help message with available commands."""
        return """**💡 Chat Commands & Tips:**

**Questions you can ask:**
• "What are people saying about [topic]?"
• "Show me negative comments about [keyword]"
• "What are the main complaints?"
• "Find highly upvoted posts about [topic]"
• "What trends do you see over time?"

**Special Commands:**
• `show full context for [ID]` - Get complete post/comment details
• `help` - Show this help message

**Search Modes:**
• **Keyword:** Fast, exact matches (free)
• **Semantic:** Understands concepts (may require indexing)

**Source References:**
When I mention specific posts/comments, I'll show their IDs like (Post ID: abc123). You can ask for full context using these IDs.

Just ask naturally - I'll search your analysis data and provide detailed answers with source citations! 🔍"""


# Global chat agent instance
chat_agent = ChatAgent()
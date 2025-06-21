"""
Chat Agent Service

Enhanced conversational AI for exploring Reddit analysis data with
natural discussion understanding and improved context navigation.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from ...database import db, ChatSession, ChatMessage
from .rag_engine import rag_engine
from .content_formatter import content_formatter


@dataclass
class ChatResponse:
    """Enhanced response from chat agent with discussion context."""
    message: str                   # Assistant's response
    sources: List[Dict[str, Any]]  # Source attributions with full discussion context
    search_type: str              # Search method used
    discussions_found: int        # Number of complete discussions found
    tokens_used: int              # Tokens used for this response
    cost_estimate: float          # Cost estimate for this response
    session_id: str               # Chat session ID


class ChatAgent:
    """
    Enhanced chat agent for conversational analysis exploration with
    natural Reddit discussion understanding and context navigation.
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
        
        # Send enhanced welcome message
        welcome_message = self._create_enhanced_welcome_message(analysis_session)
        
        db.save_chat_message(
            chat_session_id=chat_session_id,
            role='assistant',
            content=welcome_message
        )
        
        return chat_session_id
    
    def send_message(self, chat_session_id: str, user_message: str, 
                    search_type: str = 'keyword') -> ChatResponse:
        """
        Send a message and get enhanced response from chat agent.
        
        Args:
            chat_session_id: Chat session ID
            user_message: User's message
            search_type: Search method to use
        
        Returns:
            Enhanced ChatResponse with discussion context
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
        
        # Check for special commands first
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
                discussions_found=len(special_response.get('sources', [])),
                tokens_used=special_response.get('tokens_used', 0),
                cost_estimate=special_response.get('cost_estimate', 0.0),
                session_id=chat_session_id
            )
        
        # Use enhanced RAG to answer the question
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
                discussions_found=rag_response.discussions_used,
                tokens_used=rag_response.tokens_used,
                cost_estimate=rag_response.cost_estimate,
                session_id=chat_session_id
            )
            
        except Exception as e:
            error_message = f"I encountered an error while processing your question: {str(e)}\n\nTry rephrasing your question or asking about a different aspect of your data."
            
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
                discussions_found=0,
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
            Dictionary with enhanced search type availability
        """
        # Get chat session and analysis session
        chat_session = self._get_chat_session(chat_session_id)
        if not chat_session:
            raise ValueError(f"Chat session not found: {chat_session_id}")
        
        analysis_session = db.get_analysis_session(chat_session.analysis_session_id)
        collection_ids = json.loads(analysis_session.collection_ids)
        
        return rag_engine.get_available_search_types(collection_ids)
    
    def explore_discussion(self, chat_session_id: str, content_id: str, 
                          content_type: str) -> Optional[Dict[str, Any]]:
        """
        Get complete discussion context for exploration.
        
        Args:
            chat_session_id: Chat session ID
            content_id: Content ID to explore
            content_type: 'post' or 'comment'
        
        Returns:
            Complete discussion context or None if not found
        """
        # Get chat session and analysis session
        chat_session = self._get_chat_session(chat_session_id)
        if not chat_session:
            return None
        
        analysis_session = db.get_analysis_session(chat_session.analysis_session_id)
        collection_ids = json.loads(analysis_session.collection_ids)
        
        # Try to find the content in any of the collections
        from .discussion_builder import discussion_builder
        
        for collection_id in collection_ids:
            try:
                if content_type == 'post':
                    discussion = discussion_builder.build_discussion_from_post(content_id, collection_id)
                else:
                    discussion = discussion_builder.build_discussion_from_comment(content_id, collection_id)
                
                if discussion.get('post'):
                    # Format for display
                    formatted_discussion = content_formatter.format_discussion_thread(discussion)
                    return {
                        'discussion_data': discussion,
                        'formatted_text': formatted_discussion,
                        'collection_id': collection_id
                    }
            except Exception:
                continue
        
        return None
    
    def get_discussion_summary(self, chat_session_id: str) -> Dict[str, Any]:
        """
        Get a summary of the types of discussions available in this analysis.
        
        Args:
            chat_session_id: Chat session ID
        
        Returns:
            Summary of available discussion types and topics
        """
        # Get chat session and analysis session
        chat_session = self._get_chat_session(chat_session_id)
        if not chat_session:
            return {}
        
        analysis_session = db.get_analysis_session(chat_session_id)
        if not analysis_session:
            return {}
        
        keywords = json.loads(analysis_session.keywords)
        collection_ids = json.loads(analysis_session.collection_ids)
        
        # Get some representative examples
        examples = rag_engine.get_representative_examples(collection_ids, keywords, limit=3)
        
        summary = {
            'total_keywords': len(keywords),
            'total_collections': len(collection_ids),
            'total_mentions': analysis_session.total_mentions,
            'avg_sentiment': analysis_session.avg_sentiment,
            'sample_discussions': []
        }
        
        for example in examples:
            post_data = example.get('discussion_data', {}).get('post', {})
            summary['sample_discussions'].append({
                'title': post_data.get('title', 'Unknown'),
                'subreddit': post_data.get('subreddit', 'unknown'),
                'comment_count': example.get('comment_count', 0),
                'post_id': post_data.get('reddit_id', '')
            })
        
        return summary
    
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
            messages = db.get_chat_messages(session.id, limit=5)
            
            # Create preview from first user message
            preview = "New chat session"
            for message in reversed(messages):
                if message.role == 'user':
                    preview = message.content[:100] + "..." if len(message.content) > 100 else message.content
                    break
            
            # Count total messages
            total_messages = len(db.get_chat_messages(session.id, limit=1000))
            
            session_summaries.append({
                'session_id': session.id,
                'created_at': session.created_at,
                'last_active': session.last_active,
                'preview': preview,
                'message_count': total_messages
            })
        
        return session_summaries
    
    def _get_chat_session(self, chat_session_id: str) -> Optional[ChatSession]:
        """Get chat session from database."""
        session = db.get_session()
        try:
            return session.query(ChatSession).filter(ChatSession.id == chat_session_id).first()
        finally:
            session.close()
    
    def _create_enhanced_welcome_message(self, analysis_session) -> str:
        """Create enhanced welcome message for new chat session."""
        keywords = json.loads(analysis_session.keywords)
        keywords_text = ", ".join(keywords[:5])
        if len(keywords) > 5:
            keywords_text += f" (and {len(keywords) - 5} more)"
        
        # Get some quick stats about discussions
        collection_ids = json.loads(analysis_session.collection_ids)
        available_search_types = rag_engine.get_available_search_types(collection_ids)
        
        # Count available search methods
        available_methods = [name for name, info in available_search_types.items() if info['available']]
        
        return f"""👋 Welcome to your enhanced analysis chat session!

**Analysis:** {analysis_session.name}
**Keywords:** {keywords_text}
**Total Mentions:** {analysis_session.total_mentions:,}
**Avg Sentiment:** {analysis_session.avg_sentiment:+.3f}

🔍 **Available Search Methods:** {', '.join(available_methods)}

I can help you explore your Reddit discussion data in natural conversation. I now have access to complete discussion threads with full context, so I can provide much richer insights.

**Great questions to ask:**
• "What are people actually saying about [topic]?"
• "Show me discussions where people are frustrated about [keyword]"
• "What are the main complaints in these conversations?"
• "Find posts where people are praising [topic]"
• "What patterns do you see in how people discuss [keyword]?"
• "Show me examples of positive vs negative sentiment"

**New Features:**
• **Full Discussion Context** - I can see complete Reddit threads, not just fragments
• **Natural Conversations** - I understand how Reddit discussions flow
• **Real Examples** - I can quote actual user comments and conversations
• **Discussion Navigation** - Ask me to show full context for any post or comment I mention

Type your first question to start exploring your data! 🚀"""
    
    def _handle_special_commands(self, message: str, chat_session_id: str, 
                                analysis_session) -> Optional[Dict[str, Any]]:
        """Handle special commands with enhanced discussion navigation."""
        message_lower = message.lower().strip()
        
        # Handle discussion exploration requests
        if message_lower.startswith(('explore discussion', 'show discussion', 'full discussion')):
            # Extract content ID
            parts = message.split()
            if len(parts) >= 3:
                content_id = parts[-1]
                
                # Try to determine content type from context
                content_type = 'post'  # Default
                if 'comment' in message_lower:
                    content_type = 'comment'
                
                discussion = self.explore_discussion(chat_session_id, content_id, content_type)
                if discussion:
                    response = self._format_full_discussion(discussion)
                    return {
                        'message': response,
                        'sources': [{'discussion_context': discussion['discussion_data']}],
                        'tokens_used': 0,
                        'cost_estimate': 0.0
                    }
                else:
                    return {
                        'message': f"I couldn't find a discussion with ID '{content_id}' in your analysis data.",
                        'sources': [],
                        'tokens_used': 0,
                        'cost_estimate': 0.0
                    }
        
        # Handle full context requests (backward compatibility)
        if message_lower.startswith(('show full context for', 'full context for', 'show context for')):
            content_id = message.split()[-1]
            
            # Try both post and comment
            for content_type in ['post', 'comment']:
                discussion = self.explore_discussion(chat_session_id, content_id, content_type)
                if discussion:
                    response = self._format_full_discussion(discussion)
                    return {
                        'message': response,
                        'sources': [{'discussion_context': discussion['discussion_data']}],
                        'tokens_used': 0,
                        'cost_estimate': 0.0
                    }
            
            return {
                'message': f"I couldn't find content with ID '{content_id}' in your analysis data.",
                'sources': [],
                'tokens_used': 0,
                'cost_estimate': 0.0
            }
        
        # Handle summary requests
        if message_lower in ['summary', 'overview', 'what data do we have', 'data summary']:
            summary = self.get_discussion_summary(chat_session_id)
            if summary:
                response = self._format_data_summary(summary)
                return {
                    'message': response,
                    'sources': [],
                    'tokens_used': 0,
                    'cost_estimate': 0.0
                }
        
        # Handle help requests
        if message_lower in ['help', '/help', 'commands', 'what can you do']:
            return {
                'message': self._get_enhanced_help_message(),
                'sources': [],
                'tokens_used': 0,
                'cost_estimate': 0.0
            }
        
        return None
    
    def _format_full_discussion(self, discussion: Dict[str, Any]) -> str:
        """Format complete discussion for display."""
        formatted_text = discussion['formatted_text']
        
        discussion_data = discussion['discussion_data']
        post_data = discussion_data.get('post', {})
        comments_count = len(discussion_data.get('comments', []))
        
        header = f"**COMPLETE DISCUSSION**\n"
        header += f"Collection: {discussion['collection_id']}\n"
        header += f"Comments shown: {comments_count}\n"
        header += f"Discussion type: {discussion_data.get('discussion_type', 'unknown')}\n\n"
        
        return header + formatted_text
    
    def _format_data_summary(self, summary: Dict[str, Any]) -> str:
        """Format data summary for display."""
        response = f"**📊 DATA OVERVIEW**\n\n"
        response += f"**Analysis Scope:**\n"
        response += f"• {summary['total_keywords']} keywords analyzed\n"
        response += f"• {summary['total_collections']} data collections\n"
        response += f"• {summary['total_mentions']:,} total keyword mentions\n"
        response += f"• {summary['avg_sentiment']:+.3f} average sentiment\n\n"
        
        if summary.get('sample_discussions'):
            response += f"**Sample Discussions Available:**\n"
            for i, disc in enumerate(summary['sample_discussions'], 1):
                response += f"{i}. r/{disc['subreddit']}: \"{disc['title'][:60]}...\"\n"
                response += f"   ({disc['comment_count']} comments, Post ID: {disc['post_id']})\n"
        
        response += f"\n💬 Ask me about any aspect of these discussions!"
        return response
    
    def _get_enhanced_help_message(self) -> str:
        """Get enhanced help message with new features."""
        return """**💡 Enhanced Chat Features & Commands:**

**Natural Questions (Enhanced):**
• "What are people saying about [topic]?" - Get real discussion examples
• "Show me negative comments about [keyword]" - Find sentiment-specific content
• "What frustrates users about [topic]?" - Discover pain points from actual conversations
• "Find discussions where people love [keyword]" - Locate positive conversations
• "What are the main themes in discussions about [topic]?" - Identify patterns

**Discussion Navigation (New):**
• `explore discussion [ID]` - See complete discussion thread with full context
• `show full context for [ID]` - Get complete post/comment details
• `summary` - Overview of your available discussion data

**Search Modes:**
• **Keyword:** Fast exact matches with full discussion context
• **Semantic:** Understanding concepts and context (requires indexing)

**Enhanced Capabilities:**
✅ **Complete Discussion Threads** - I can see full Reddit conversations, not fragments
✅ **Natural Context** - I understand how posts and comments relate to each other  
✅ **Real User Quotes** - I can provide actual quotes from your Reddit discussions
✅ **Conversation Flow** - I understand Reddit's comment threading and responses
✅ **Rich Attribution** - When I mention content, I provide IDs for further exploration

**Example Workflow:**
1. Ask: "What complaints do people have about customer service?"
2. I'll find relevant discussions and quote actual user comments
3. Ask: "show full context for [Post ID]" to see complete threads
4. Continue exploring with follow-up questions about specific aspects

Just ask naturally - I'll search your Reddit data and provide detailed answers with real conversation examples! 🔍"""


# Global chat agent instance
chat_agent = ChatAgent()
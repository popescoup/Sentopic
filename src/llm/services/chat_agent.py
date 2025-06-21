"""
Chat Agent Service

Enhanced conversational AI with analytics awareness for exploring Reddit analysis data
with intelligent query routing and natural discussion understanding.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from ...database import db, ChatSession, ChatMessage
from .rag_engine import rag_engine
from .content_formatter import content_formatter
from .query_classifier import query_classifier
from .analytics_search_engine import analytics_search_engine


@dataclass
class ChatResponse:
    """Enhanced response from chat agent with analytics and discussion context."""
    message: str                   # Assistant's response
    sources: List[Dict[str, Any]]  # Source attributions with full discussion context
    analytics_insights: Dict[str, Any]  # Analytics data used in response
    search_type: str              # Search method used
    discussions_found: int        # Number of complete discussions found
    tokens_used: int              # Tokens used for this response
    cost_estimate: float          # Cost estimate for this response
    session_id: str               # Chat session ID
    query_classification: Dict[str, Any]  # How the query was classified and routed


class ChatAgent:
    """
    Enhanced chat agent with analytics awareness for conversational analysis exploration.
    
    Intelligently routes queries between analytics data and discussion content
    to provide optimal responses based on user intent.
    """
    
    def __init__(self):
        self.max_context_messages = 10  # 5 user + 5 assistant pairs
    
    def start_chat_session(self, analysis_session_id: str) -> str:
        """
        Start a new analytics-aware chat session for an analysis session.
        
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
        
        # Send enhanced welcome message with analytics awareness
        welcome_message = self._create_analytics_aware_welcome_message(analysis_session)
        
        db.save_chat_message(
            chat_session_id=chat_session_id,
            role='assistant',
            content=welcome_message
        )
        
        return chat_session_id
    
    def send_message(self, chat_session_id: str, user_message: str, 
                    search_type: str = 'auto') -> ChatResponse:
        """
        Send a message and get analytics-aware response from chat agent.
        
        Args:
            chat_session_id: Chat session ID
            user_message: User's message
            search_type: Search method ('auto' for intelligent routing, or specific type)
        
        Returns:
            Enhanced ChatResponse with analytics and discussion context
        """
        # Validate chat session
        chat_session = self._get_chat_session(chat_session_id)
        if not chat_session:
            raise ValueError(f"Chat session not found: {chat_session_id}")
        
        # Get analysis session info
        analysis_session = db.get_analysis_session(chat_session.analysis_session_id)
        collection_ids = json.loads(analysis_session.collection_ids)
        available_keywords = json.loads(analysis_session.keywords)
        
        # Save user message
        db.save_chat_message(
            chat_session_id=chat_session_id,
            role='user',
            content=user_message
        )
        
        # Check for special commands first
        special_response = self._handle_enhanced_special_commands(
            user_message, chat_session_id, analysis_session
        )
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
                analytics_insights=special_response.get('analytics_insights', {}),
                search_type='command',
                discussions_found=len(special_response.get('sources', [])),
                tokens_used=special_response.get('tokens_used', 0),
                cost_estimate=special_response.get('cost_estimate', 0.0),
                session_id=chat_session_id,
                query_classification=special_response.get('query_classification', {})
            )
        
        # Classify the query for intelligent routing
        classification = query_classifier.classify_query(user_message, available_keywords)
        
        # Use enhanced RAG with analytics awareness
        try:
            rag_response = rag_engine.answer_question(
                question=user_message,
                collection_ids=collection_ids,
                search_type=search_type,
                max_results=5
            )
            
            # Enhance response with chat context if needed
            enhanced_response = self._enhance_response_with_chat_context(
                rag_response, user_message, chat_session_id
            )
            
            # Save assistant response
            db.save_chat_message(
                chat_session_id=chat_session_id,
                role='assistant',
                content=enhanced_response.answer,
                tokens_used=enhanced_response.tokens_used,
                cost_estimate=enhanced_response.cost_estimate
            )
            
            return ChatResponse(
                message=enhanced_response.answer,
                sources=enhanced_response.sources,
                analytics_insights=enhanced_response.analytics_insights,
                search_type=enhanced_response.search_type,
                discussions_found=enhanced_response.discussions_used,
                tokens_used=enhanced_response.tokens_used,
                cost_estimate=enhanced_response.cost_estimate,
                session_id=chat_session_id,
                query_classification=enhanced_response.query_classification
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
                analytics_insights={},
                search_type=search_type,
                discussions_found=0,
                tokens_used=0,
                cost_estimate=0.0,
                session_id=chat_session_id,
                query_classification={'type': 'error', 'confidence': 0.0}
            )
    
    def get_analytics_overview(self, chat_session_id: str, 
                             keyword: Optional[str] = None) -> Dict[str, Any]:
        """
        Get analytics overview for a keyword or general overview.
        
        Args:
            chat_session_id: Chat session ID
            keyword: Optional specific keyword to analyze
        
        Returns:
            Analytics overview data
        """
        # Get chat session and analysis session
        chat_session = self._get_chat_session(chat_session_id)
        if not chat_session:
            raise ValueError(f"Chat session not found: {chat_session_id}")
        
        analysis_session = db.get_analysis_session(chat_session.analysis_session_id)
        collection_ids = json.loads(analysis_session.collection_ids)
        
        if keyword:
            # Get specific keyword overview
            return analytics_search_engine.get_keyword_overview(keyword, collection_ids)
        else:
            # Get general analytics insights
            return analytics_search_engine.search_by_analytics_insights(
                collection_ids, 'most_frequent', limit=10
            )
    
    def explore_keyword_analytically(self, chat_session_id: str, keyword: str) -> Dict[str, Any]:
        """
        Get comprehensive analytics exploration for a keyword.
        
        Args:
            chat_session_id: Chat session ID
            keyword: Keyword to explore
        
        Returns:
            Comprehensive keyword analytics with examples
        """
        # Get chat session and analysis session
        chat_session = self._get_chat_session(chat_session_id)
        if not chat_session:
            raise ValueError(f"Chat session not found: {chat_session_id}")
        
        analysis_session = db.get_analysis_session(chat_session.analysis_session_id)
        collection_ids = json.loads(analysis_session.collection_ids)
        
        # Get keyword overview
        keyword_overview = analytics_search_engine.get_keyword_overview(keyword, collection_ids)
        
        # Get specific examples
        examples = analytics_search_engine.search_by_keyword_analytics(
            keyword, collection_ids, limit=5
        )
        
        # Enrich with discussion contexts
        examples = analytics_search_engine.enrich_with_discussion_context(examples)
        
        return {
            'keyword': keyword,
            'overview': keyword_overview,
            'examples': examples,
            'found': keyword_overview.get('found', False)
        }
    
    def get_chat_history(self, chat_session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for a session with enhanced metadata."""
        messages = db.get_chat_messages(chat_session_id, limit)
        
        formatted_messages = []
        for message in reversed(messages):
            formatted_messages.append({
                'role': message.role,
                'content': message.content,
                'timestamp': message.timestamp,
                'tokens_used': message.tokens_used,
                'cost_estimate': message.cost_estimate
            })
        
        return formatted_messages
    
    def get_available_search_types(self, chat_session_id: str) -> Dict[str, Dict[str, Any]]:
        """Get available search types including analytics-driven search."""
        chat_session = self._get_chat_session(chat_session_id)
        if not chat_session:
            raise ValueError(f"Chat session not found: {chat_session_id}")
        
        analysis_session = db.get_analysis_session(chat_session.analysis_session_id)
        collection_ids = json.loads(analysis_session.collection_ids)
        
        return rag_engine.get_available_search_types(collection_ids)
    
    def explore_discussion(self, chat_session_id: str, content_id: str, 
                          content_type: str) -> Optional[Dict[str, Any]]:
        """Get complete discussion context for exploration."""
        chat_session = self._get_chat_session(chat_session_id)
        if not chat_session:
            return None
        
        analysis_session = db.get_analysis_session(chat_session.analysis_session_id)
        collection_ids = json.loads(analysis_session.collection_ids)
        
        from .discussion_builder import discussion_builder
        
        for collection_id in collection_ids:
            try:
                if content_type == 'post':
                    discussion = discussion_builder.build_discussion_from_post(content_id, collection_id)
                else:
                    discussion = discussion_builder.build_discussion_from_comment(content_id, collection_id)
                
                if discussion.get('post'):
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
        """Get enhanced summary with analytics insights."""
        chat_session = self._get_chat_session(chat_session_id)
        if not chat_session:
            return {}
        
        analysis_session = db.get_analysis_session(chat_session.analysis_session_id)
        if not analysis_session:
            return {}
        
        keywords = json.loads(analysis_session.keywords)
        collection_ids = json.loads(analysis_session.collection_ids)
        
        # Get analytics insights
        top_keywords_data = analytics_search_engine.search_by_analytics_insights(
            collection_ids, 'most_frequent', limit=5
        )
        
        # Get representative examples
        examples = rag_engine.get_representative_examples(collection_ids, keywords, limit=3)
        
        summary = {
            'total_keywords': len(keywords),
            'total_collections': len(collection_ids),
            'total_mentions': analysis_session.total_mentions,
            'avg_sentiment': analysis_session.avg_sentiment,
            'top_keywords': [
                {
                    'keyword': result.keyword,
                    'analytics_metadata': result.analytics_metadata
                }
                for result in top_keywords_data[:5]
            ],
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
        """List all chat sessions for an analysis session."""
        chat_sessions = db.get_chat_sessions(analysis_session_id)
        
        session_summaries = []
        for session in chat_sessions:
            messages = db.get_chat_messages(session.id, limit=5)
            
            preview = "New analytics-aware chat session"
            for message in reversed(messages):
                if message.role == 'user':
                    preview = message.content[:100] + "..." if len(message.content) > 100 else message.content
                    break
            
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
    
    def _create_analytics_aware_welcome_message(self, analysis_session) -> str:
        """Create analytics-aware welcome message for new chat session."""
        keywords = json.loads(analysis_session.keywords)
        collection_ids = json.loads(analysis_session.collection_ids)
        
        keywords_text = ", ".join(keywords[:5])
        if len(keywords) > 5:
            keywords_text += f" (and {len(keywords) - 5} more)"
        
        # Get analytics overview
        try:
            top_keywords = analytics_search_engine.search_by_analytics_insights(
                collection_ids, 'most_frequent', limit=3
            )
            top_keywords_text = ", ".join([f"'{result.keyword}'" for result in top_keywords[:3]])
        except:
            top_keywords_text = "data available"
        
        # Get available search types
        available_search_types = rag_engine.get_available_search_types(collection_ids)
        available_methods = [name for name, info in available_search_types.items() if info['available']]
        
        return f"""👋 Welcome to your **Analytics-Aware Chat Session**!

**Analysis:** {analysis_session.name}
**Keywords:** {keywords_text}
**Total Mentions:** {analysis_session.total_mentions:,}
**Avg Sentiment:** {analysis_session.avg_sentiment:+.3f}
**Top Keywords:** {top_keywords_text}

🔍 **Available Search Methods:** {', '.join(available_methods)}
🧠 **Analytics Awareness:** I can now reference your exact keyword frequencies, sentiment scores, co-occurrences, and trends!

**NEW: Analytics-Powered Questions You Can Ask:**
• "Why does '{keywords[0] if keywords else 'time'}' appear so frequently in my data?"
• "What's the sentiment breakdown for '{keywords[1] if len(keywords) > 1 else 'garden'}'?"
• "Show me examples where '{keywords[0] if keywords else 'time'}' has negative sentiment"
• "Which keywords co-occur most often with '{keywords[0] if keywords else 'time'}'?"
• "What are the exact statistics for '{keywords[0] if keywords else 'time'}' mentions?"
• "Compare the frequency of '{keywords[0] if keywords else 'time'}' vs '{keywords[1] if len(keywords) > 1 else 'space'}'"

**Also Great For Discussion Questions:**
• "What are people actually saying about [topic]?"
• "Show me discussions where people are frustrated about [keyword]"
• "Find examples of positive conversations about [keyword]"

**Enhanced Features:**
✅ **Analytics Integration** - I know your exact keyword statistics and can explain patterns
✅ **Smart Query Routing** - I automatically detect if you want analytics data vs. discussion examples
✅ **Complete Discussion Context** - Full Reddit threads with analytical insights
✅ **Precise Attribution** - Exact mention counts, sentiment scores, and co-occurrence data

**Example Workflow:**
1. Ask: "Why does 'time' appear more than any other keyword?"
2. I'll show you the exact frequency data and sentiment patterns
3. Then provide real discussion examples where 'time' appears
4. Ask follow-ups like "show full context for [Post ID]" to explore specific threads

Type your first question and I'll intelligently route it to the best data sources! 🚀📊"""
    
    def _handle_enhanced_special_commands(self, message: str, chat_session_id: str, 
                                        analysis_session) -> Optional[Dict[str, Any]]:
        """Handle special commands with analytics awareness."""
        message_lower = message.lower().strip()
        
        # Analytics overview commands
        if message_lower in ['analytics', 'analytics overview', 'keyword stats', 'show analytics']:
            return self._handle_analytics_overview_command(chat_session_id, analysis_session)
        
        # Keyword exploration commands
        keyword_explore_match = self._extract_keyword_explore_command(message_lower)
        if keyword_explore_match:
            return self._handle_keyword_exploration_command(
                chat_session_id, keyword_explore_match, analysis_session
            )
        
        # Discussion exploration requests
        if message_lower.startswith(('explore discussion', 'show discussion', 'full discussion')):
            parts = message.split()
            if len(parts) >= 3:
                content_id = parts[-1]
                content_type = 'post'
                if 'comment' in message_lower:
                    content_type = 'comment'
                
                discussion = self.explore_discussion(chat_session_id, content_id, content_type)
                if discussion:
                    response = self._format_full_discussion(discussion)
                    return {
                        'message': response,
                        'sources': [{'discussion_context': discussion['discussion_data']}],
                        'analytics_insights': {},
                        'tokens_used': 0,
                        'cost_estimate': 0.0,
                        'query_classification': {'type': 'command', 'confidence': 1.0}
                    }
                else:
                    return {
                        'message': f"I couldn't find a discussion with ID '{content_id}' in your analysis data.",
                        'sources': [],
                        'analytics_insights': {},
                        'tokens_used': 0,
                        'cost_estimate': 0.0,
                        'query_classification': {'type': 'command', 'confidence': 1.0}
                    }
        
        # Enhanced summary requests
        if message_lower in ['summary', 'overview', 'what data do we have', 'data summary']:
            summary = self.get_discussion_summary(chat_session_id)
            if summary:
                response = self._format_enhanced_data_summary(summary)
                return {
                    'message': response,
                    'sources': [],
                    'analytics_insights': summary,
                    'tokens_used': 0,
                    'cost_estimate': 0.0,
                    'query_classification': {'type': 'command', 'confidence': 1.0}
                }
        
        # Help requests
        if message_lower in ['help', '/help', 'commands', 'what can you do']:
            return {
                'message': self._get_analytics_aware_help_message(),
                'sources': [],
                'analytics_insights': {},
                'tokens_used': 0,
                'cost_estimate': 0.0,
                'query_classification': {'type': 'command', 'confidence': 1.0}
            }
        
        return None
    
    def _handle_analytics_overview_command(self, chat_session_id: str, 
                                         analysis_session) -> Dict[str, Any]:
        """Handle analytics overview command."""
        collection_ids = json.loads(analysis_session.collection_ids)
        
        # Get top keywords analytics
        top_keywords = analytics_search_engine.search_by_analytics_insights(
            collection_ids, 'most_frequent', limit=10
        )
        
        # Get most positive and negative keywords
        positive_keywords = analytics_search_engine.search_by_analytics_insights(
            collection_ids, 'most_positive', limit=5
        )
        negative_keywords = analytics_search_engine.search_by_analytics_insights(
            collection_ids, 'most_negative', limit=5
        )
        
        response = self._format_analytics_overview(top_keywords, positive_keywords, negative_keywords)
        
        analytics_insights = {
            'top_keywords': [{'keyword': r.keyword, 'metadata': r.analytics_metadata} for r in top_keywords],
            'positive_keywords': [{'keyword': r.keyword, 'metadata': r.analytics_metadata} for r in positive_keywords],
            'negative_keywords': [{'keyword': r.keyword, 'metadata': r.analytics_metadata} for r in negative_keywords]
        }
        
        return {
            'message': response,
            'sources': [],
            'analytics_insights': analytics_insights,
            'tokens_used': 0,
            'cost_estimate': 0.0,
            'query_classification': {'type': 'command', 'confidence': 1.0}
        }
    
    def _extract_keyword_explore_command(self, message: str) -> Optional[str]:
        """Extract keyword from exploration commands."""
        import re
        
        patterns = [
            r'explore keyword ["\']?([^"\']+)["\']?',
            r'analyze ["\']?([^"\']+)["\']?',
            r'keyword analysis ["\']?([^"\']+)["\']?',
            r'tell me about ["\']?([^"\']+)["\']?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _handle_keyword_exploration_command(self, chat_session_id: str, keyword: str, 
                                          analysis_session) -> Dict[str, Any]:
        """Handle keyword exploration command."""
        exploration_data = self.explore_keyword_analytically(chat_session_id, keyword)
        
        if not exploration_data['found']:
            return {
                'message': f"The keyword '{keyword}' was not found in your analysis data. Available keywords include those from your original analysis.",
                'sources': [],
                'analytics_insights': {},
                'tokens_used': 0,
                'cost_estimate': 0.0,
                'query_classification': {'type': 'command', 'confidence': 1.0}
            }
        
        response = self._format_keyword_exploration(exploration_data)
        
        return {
            'message': response,
            'sources': [{'analytics_exploration': exploration_data}],
            'analytics_insights': exploration_data['overview'],
            'tokens_used': 0,
            'cost_estimate': 0.0,
            'query_classification': {'type': 'command', 'confidence': 1.0}
        }
    
    def _enhance_response_with_chat_context(self, rag_response, user_message: str, 
                                          chat_session_id: str):
        """Enhance RAG response with chat context if needed."""
        # For now, return as-is, but this could add conversation context
        return rag_response
    
    def _format_analytics_overview(self, top_keywords, positive_keywords, negative_keywords) -> str:
        """Format analytics overview for display."""
        response = "📊 **COMPREHENSIVE ANALYTICS OVERVIEW**\n\n"
        
        # Top keywords by frequency
        response += "**🔥 Most Frequently Mentioned Keywords:**\n"
        for i, result in enumerate(top_keywords[:5], 1):
            metadata = result.analytics_metadata
            response += f"{i}. **{result.keyword}**: {metadata.get('keyword_total_mentions', 'N/A')} mentions "
            response += f"(Sentiment: {metadata.get('keyword_avg_sentiment', 0):+.3f})\n"
        
        # Most positive keywords
        if positive_keywords:
            response += "\n**😊 Most Positive Keywords:**\n"
            for i, result in enumerate(positive_keywords[:3], 1):
                metadata = result.analytics_metadata
                response += f"{i}. **{result.keyword}**: {metadata.get('keyword_avg_sentiment', 0):+.3f} sentiment "
                response += f"({metadata.get('keyword_total_mentions', 'N/A')} mentions)\n"
        
        # Most negative keywords
        if negative_keywords:
            response += "\n**😔 Most Negative Keywords:**\n"
            for i, result in enumerate(negative_keywords[:3], 1):
                metadata = result.analytics_metadata
                response += f"{i}. **{result.keyword}**: {metadata.get('keyword_avg_sentiment', 0):+.3f} sentiment "
                response += f"({metadata.get('keyword_total_mentions', 'N/A')} mentions)\n"
        
        response += "\n💡 **Ask me about any specific keyword for detailed analysis!**"
        return response
    
    def _format_keyword_exploration(self, exploration_data: Dict[str, Any]) -> str:
        """Format keyword exploration data for display."""
        keyword = exploration_data['keyword']
        overview = exploration_data['overview']
        examples = exploration_data['examples']
        
        response = f"🔍 **DETAILED ANALYSIS: '{keyword}'**\n\n"
        
        # Basic statistics
        response += f"**📊 Key Statistics:**\n"
        response += f"• Total mentions: {overview['total_mentions']:,}\n"
        response += f"• Average sentiment: {overview['avg_sentiment']:+.3f}\n"
        response += f"• Found in {overview['collections_found']} collection(s)\n"
        
        # Distribution
        if overview.get('mention_distribution'):
            dist = overview['mention_distribution']
            response += f"• Distribution: {dist.get('post', 0)} posts, {dist.get('comment', 0)} comments\n"
        
        # Sentiment breakdown
        if overview.get('sentiment_distribution'):
            sent_dist = overview['sentiment_distribution']
            total = sum(sent_dist.values())
            if total > 0:
                pos_pct = (sent_dist['positive'] + sent_dist['very_positive']) / total * 100
                neg_pct = (sent_dist['negative'] + sent_dist['very_negative']) / total * 100
                response += f"• Sentiment: {pos_pct:.1f}% positive, {neg_pct:.1f}% negative\n"
        
        # Co-occurrences
        if overview.get('top_cooccurrences'):
            cooccur_list = [f"'{co['keyword']}' ({co['count']})" for co in overview['top_cooccurrences'][:3]]
            response += f"• Often appears with: {', '.join(cooccur_list)}\n"
        
        # Examples
        if examples:
            response += f"\n**💬 Representative Examples:**\n"
            for i, example in enumerate(examples[:3], 1):
                response += f"\n{i}. Sentiment: {example.sentiment_score:+.3f}\n"
                response += f"   Context: {example.mention_context[:150]}...\n"
                if example.analytics_metadata.get('post_title'):
                    response += f"   Post: \"{example.analytics_metadata['post_title'][:50]}...\"\n"
        
        response += f"\n💡 **Ask follow-up questions like:** \"Show me negative examples of '{keyword}'\" or \"What discussions mention '{keyword}' most?\""
        
        return response
    
    def _format_full_discussion(self, discussion: Dict[str, Any]) -> str:
        """Format complete discussion for display."""
        formatted_text = discussion['formatted_text']
        
        discussion_data = discussion['discussion_data']
        post_data = discussion_data.get('post', {})
        comments_count = len(discussion_data.get('comments', []))
        
        header = f"**📝 COMPLETE DISCUSSION**\n"
        header += f"Collection: {discussion['collection_id']}\n"
        header += f"Comments shown: {comments_count}\n"
        header += f"Discussion type: {discussion_data.get('discussion_type', 'unknown')}\n\n"
        
        return header + formatted_text
    
    def _format_enhanced_data_summary(self, summary: Dict[str, Any]) -> str:
        """Format enhanced data summary with analytics insights."""
        response = f"**📊 ENHANCED DATA OVERVIEW**\n\n"
        response += f"**Analysis Scope:**\n"
        response += f"• {summary['total_keywords']} keywords analyzed\n"
        response += f"• {summary['total_collections']} data collections\n"
        response += f"• {summary['total_mentions']:,} total keyword mentions\n"
        response += f"• {summary['avg_sentiment']:+.3f} average sentiment\n\n"
        
        # Top keywords with analytics
        if summary.get('top_keywords'):
            response += f"**🔥 Top Keywords by Frequency:**\n"
            for i, kw_data in enumerate(summary['top_keywords'], 1):
                metadata = kw_data.get('analytics_metadata', {})
                response += f"{i}. **{kw_data['keyword']}**: {metadata.get('keyword_total_mentions', 'N/A')} mentions\n"
        
        # Sample discussions
        if summary.get('sample_discussions'):
            response += f"\n**💬 Sample Discussions Available:**\n"
            for i, disc in enumerate(summary['sample_discussions'], 1):
                response += f"{i}. r/{disc['subreddit']}: \"{disc['title'][:60]}...\"\n"
                response += f"   ({disc['comment_count']} comments, Post ID: {disc['post_id']})\n"
        
        response += f"\n💬 Ask me analytical questions or request specific discussion examples!"
        return response
    
    def _get_analytics_aware_help_message(self) -> str:
        """Get analytics-aware help message with new features."""
        return """**💡 Analytics-Aware Chat Features & Commands:**

**🔥 NEW: Analytics Questions:**
• `analytics` - Get comprehensive analytics overview
• `explore keyword "time"` - Deep dive into specific keyword analytics
• "Why does [keyword] appear frequently?" - Frequency analysis with examples
• "What's the sentiment for [keyword]?" - Sentiment breakdown with real examples
• "Which keywords co-occur with [keyword]?" - Co-occurrence analysis
• "Compare [keyword1] vs [keyword2]" - Comparative analytics

**🗣️ Enhanced Discussion Questions:**
• "What are people saying about [topic]?" - Get discussions + analytics context
• "Show me negative comments about [keyword]" - Sentiment-filtered discussions
• "Find discussions where people love [keyword]" - Positive sentiment examples
• "What are the main themes about [topic]?" - Pattern analysis with statistics

**📊 Navigation & Exploration:**
• `summary` - Enhanced overview with analytics insights
• `explore discussion [ID]` - See complete discussion thread
• `show full context for [ID]` - Get complete post/comment details
• `help` - This help message

**🧠 Intelligent Query Routing:**
I automatically detect whether you want:
- **Analytics data** (frequencies, sentiment, patterns) → Routes to analytics engine
- **Discussion examples** (what people say, conversations) → Routes to discussion search
- **Both** (comprehensive insights) → Combines analytics + examples

**🔍 Search Modes Available:**
• **Analytics-Driven**: Uses your keyword analysis data (NEW!)
• **Keyword**: Fast exact matches with full discussion context
• **Semantic**: Understanding concepts and context (if indexed)

**✨ Enhanced Capabilities:**
✅ **Precise Analytics** - I know your exact keyword frequencies and sentiment scores
✅ **Smart Routing** - I detect if you want data analysis vs. discussion examples
✅ **Complete Context** - Full Reddit threads with analytical insights
✅ **Rich Attribution** - Exact mention counts, sentiment breakdowns, co-occurrences

**🎯 Example Analytics Workflow:**
1. Ask: "Why does 'time' appear more than other keywords?"
2. I'll show: exact frequency (#1 with 847 mentions), sentiment (+0.23), co-occurrences
3. Plus: real discussion examples where 'time' appears with that sentiment
4. Follow up: "show negative examples" or "explore discussion [Post ID]"

**🎯 Example Discussion Workflow:**
1. Ask: "What complaints do people have about gardening?"
2. I'll find: relevant discussions + analytics context (sentiment: -0.45, 127 mentions)
3. Plus: actual user quotes and complaint examples
4. Follow up: "show full context for [Post ID]" to explore complete threads

Just ask naturally - I'll intelligently route your question to the best data sources! 🚀📊"""


# Global chat agent instance
chat_agent = ChatAgent()
"""
RAG (Retrieval-Augmented Generation) Engine

Enhanced RAG engine that combines search results with LLM generation using
natural Reddit discussion contexts for optimal response quality.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .search_engine import SearchEngineFactory, SearchResult
from .discussion_builder import discussion_builder
from .content_formatter import content_formatter
from ...llm import get_llm_provider
from ...database import db, Post, Comment


@dataclass
class RAGResponse:
    """Enhanced response from RAG engine with sources and context."""
    answer: str                     # AI-generated answer
    sources: List[Dict[str, Any]]   # Source attributions with full context
    search_type: str               # Search method used
    search_results_count: int      # Number of search results found
    discussions_used: int          # Number of complete discussions used
    tokens_used: int               # LLM tokens used
    cost_estimate: float           # Cost estimate for this query


class RAGEngine:
    """
    Enhanced RAG engine that preserves Reddit's conversational nature.
    
    Builds complete discussion contexts and formats them naturally
    for optimal LLM understanding and response generation.
    """
    
    def __init__(self):
        self.max_discussions = 3      # Maximum complete discussions to include
        self.max_context_length = 8000  # Character limit for context
    
    def answer_question(self, question: str, collection_ids: List[str], 
                       search_type: str = 'keyword', 
                       max_results: int = 5) -> RAGResponse:
        """
        Answer a question using enhanced RAG with natural Reddit discussions.
        
        Args:
            question: User's question
            collection_ids: Collection IDs to search in
            search_type: 'keyword', 'local_semantic', or 'cloud_semantic'
            max_results: Maximum search results to process
        
Returns:
            RAGResponse with answer and rich sources
        """
        # Get search engine and perform search
        search_engine = SearchEngineFactory.create_engine(search_type)
        search_results = search_engine.search(question, collection_ids, limit=max_results)
        
        if not search_results:
            return RAGResponse(
                answer="I couldn't find any relevant discussions in your Reddit data that relate to this question. Try rephrasing your question or asking about different topics that might be covered in your collections.",
                sources=[],
                search_type=search_type,
                search_results_count=0,
                discussions_used=0,
                tokens_used=0,
                cost_estimate=0.0
            )
        
        # Build complete discussion contexts
        discussions = self._build_discussion_contexts(search_results)
        
        if not discussions:
            return RAGResponse(
                answer="I found some relevant content but couldn't build complete discussion contexts. The data might be incomplete or fragmented.",
                sources=[],
                search_type=search_type,
                search_results_count=len(search_results),
                discussions_used=0,
                tokens_used=0,
                cost_estimate=0.0
            )
        
        # Generate answer using LLM with natural discussion contexts
        llm_response = self._generate_answer_with_discussions(question, discussions)
        
        # Format sources for attribution
        sources = self._format_discussion_sources(discussions, search_results)
        
        return RAGResponse(
            answer=llm_response['content'],
            sources=sources,
            search_type=search_type,
            search_results_count=len(search_results),
            discussions_used=len(discussions),
            tokens_used=llm_response['tokens_used'],
            cost_estimate=llm_response['cost_estimate']
        )
    
    def _build_discussion_contexts(self, search_results: List[SearchResult]) -> List[Dict[str, Any]]:
        """
        Build complete discussion contexts from search results.
        
        Args:
            search_results: Raw search results
        
        Returns:
            List of complete discussion contexts
        """
        discussions = []
        processed_posts = set()  # Avoid duplicate discussions
        
        for result in search_results:
            try:
                # Build discussion context based on content type
                if result.content_type == 'post':
                    if result.content_id not in processed_posts:
                        discussion = discussion_builder.build_discussion_from_post(
                            result.content_id, result.collection_id
                        )
                        if discussion.get('post'):
                            discussions.append(discussion)
                            processed_posts.add(result.content_id)
                
                elif result.content_type == 'comment':
                    # For comments, check if we've already processed the parent post
                    parent_post_id = result.metadata.get('post_reddit_id')
                    if parent_post_id and parent_post_id not in processed_posts:
                        discussion = discussion_builder.build_discussion_from_comment(
                            result.content_id, result.collection_id
                        )
                        if discussion.get('post'):
                            discussions.append(discussion)
                            processed_posts.add(parent_post_id)
                
                # Limit number of discussions to keep context manageable
                if len(discussions) >= self.max_discussions:
                    break
                    
            except Exception as e:
                # Skip problematic results but continue processing
                continue
        
        return discussions
    
    def _generate_answer_with_discussions(self, question: str, 
                                        discussions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate answer using LLM with natural Reddit discussions.
        
        Args:
            question: User's question
            discussions: Complete discussion contexts
        
        Returns:
            Dictionary with LLM response details
        """
        # Get LLM provider
        provider = get_llm_provider()
        if not provider:
            raise RuntimeError("No LLM provider available. Please check your configuration.")
        
        # Build natural context from discussions
        context = self._build_natural_context(discussions)
        
        # Build enhanced prompts
        system_prompt = self._build_enhanced_system_prompt()
        user_prompt = self._build_enhanced_user_prompt(question, context)
        
        # Generate response
        response = provider.generate(user_prompt, system_prompt)
        
        return {
            'content': response.content,
            'tokens_used': response.tokens_used,
            'cost_estimate': response.cost_estimate,
            'provider': response.provider,
            'model': response.model
        }
    
    def _build_natural_context(self, discussions: List[Dict[str, Any]]) -> str:
        """
        Build natural conversation context from complete discussions.
        
        Args:
            discussions: Complete discussion contexts
        
        Returns:
            Naturally formatted context string
        """
        if not discussions:
            return "No relevant discussions found."
        
        context_parts = ["Here are the relevant Reddit discussions from your data:\n"]
        
        for i, discussion in enumerate(discussions, 1):
            # Format each discussion naturally
            formatted_discussion = content_formatter.format_discussion_thread(discussion)
            
            # Add discussion header
            post_title = discussion.get('post', {}).get('title', 'Unknown Post')
            subreddit = discussion.get('post', {}).get('subreddit', 'unknown')
            comment_count = len(discussion.get('comments', []))
            
            discussion_header = f"\n{'='*60}\nDISCUSSION {i}: r/{subreddit}\n{post_title}\n({comment_count} comments shown)\n{'='*60}\n"
            
            full_discussion = discussion_header + formatted_discussion
            
            # Check context length limits
            current_length = sum(len(part) for part in context_parts)
            if current_length + len(full_discussion) > self.max_context_length:
                # Truncate this discussion to fit
                remaining_space = self.max_context_length - current_length - 100  # Leave some buffer
                if remaining_space > 500:  # Only include if meaningful content can fit
                    truncated_discussion = content_formatter.format_content_for_context_window(
                        full_discussion, remaining_space
                    )
                    context_parts.append(truncated_discussion)
                break
            else:
                context_parts.append(full_discussion)
        
        return "\n".join(context_parts)
    
    def _build_enhanced_system_prompt(self) -> str:
        """Build enhanced system prompt for natural Reddit discussion analysis."""
        return """You are an expert at analyzing Reddit discussions and providing insights based on real conversations. You have access to complete Reddit discussion threads including posts and their comment conversations.

Your responses should be:
- CONVERSATIONAL: Based on actual Reddit discussions, capturing the tone and insights of real users
- SPECIFIC: Quote directly from posts and comments when relevant, using natural language
- CONTEXTUAL: Understand that posts and comments are part of ongoing conversations
- ATTRIBUTIVE: Reference specific discussions and users when making claims
- INSIGHTFUL: Identify patterns, consensus, disagreements, and notable perspectives from the discussions

When referencing Reddit content:
- Quote naturally: "One user mentioned..." or "In a discussion about X, someone said..."
- Use Post IDs and Comment IDs for attribution when helpful: (Post ID: abc123)
- Capture the conversational flow: how people respond to each other
- Note voting patterns: highly upvoted comments often represent community consensus

Format your response as a natural analysis of what the Reddit community is actually saying about the topic, with specific examples and quotes from the discussions."""
    
    def _build_enhanced_user_prompt(self, question: str, context: str) -> str:
        """Build enhanced user prompt with natural discussion context."""
        return f"""Based on these actual Reddit discussions from the user's data, please answer this question:

QUESTION: {question}

REDDIT DISCUSSIONS:
{context}

Please analyze what the Reddit community is actually saying about this topic. Include specific quotes and examples from the discussions above. Reference the Post IDs and Comment IDs when citing specific examples. Capture both the overall sentiment and any interesting disagreements or different perspectives you notice in the conversations."""
    
    def _format_discussion_sources(self, discussions: List[Dict[str, Any]], 
                                 search_results: List[SearchResult]) -> List[Dict[str, Any]]:
        """
        Format discussions as source attributions with full context.
        
        Args:
            discussions: Complete discussion contexts
            search_results: Original search results for relevance scores
        
        Returns:
            List of formatted source attributions
        """
        sources = []
        
        # Create a mapping of content IDs to relevance scores
        relevance_map = {
            (result.content_id, result.content_type): result.relevance_score 
            for result in search_results
        }
        
        for discussion in discussions:
            post_data = discussion.get('post', {})
            comments_data = discussion.get('comments', [])
            
            if post_data:
                # Get relevance score for this post
                post_relevance = relevance_map.get((post_data.get('reddit_id'), 'post'), 0.0)
                
                # Create rich source attribution for the post
                source = {
                    'content_id': post_data.get('reddit_id'),
                    'content_type': 'post',
                    'collection_id': post_data.get('collection_id'),
                    'relevance_score': post_relevance,
                    'title': post_data.get('title', ''),
                    'author': post_data.get('author', 'Unknown'),
                    'score': post_data.get('score', 0),
                    'created_utc': post_data.get('created_utc'),
                    'subreddit': post_data.get('subreddit', 'unknown'),
                    'url': post_data.get('url', ''),
                    'comment_count': len(comments_data),
                    'preview': (post_data.get('title', '') + " " + post_data.get('content', ''))[:200] + "...",
                    'discussion_type': discussion.get('discussion_type', 'unknown')
                }
                sources.append(source)
                
                # Add key comments as separate sources
                for comment in comments_data[:3]:  # Top 3 comments
                    comment_relevance = relevance_map.get((comment.get('reddit_id'), 'comment'), 0.0)
                    
                    comment_source = {
                        'content_id': comment.get('reddit_id'),
                        'content_type': 'comment',
                        'collection_id': comment.get('collection_id'),
                        'relevance_score': comment_relevance,
                        'author': comment.get('author', 'Unknown'),
                        'score': comment.get('score', 0),
                        'created_utc': comment.get('created_utc'),
                        'parent_post_id': comment.get('post_reddit_id'),
                        'parent_post_title': post_data.get('title', ''),
                        'is_root': comment.get('is_root', False),
                        'depth': comment.get('depth', 0),
                        'preview': comment.get('content', '')[:200] + "...",
                        'subreddit': post_data.get('subreddit', 'unknown')
                    }
                    sources.append(comment_source)
        
        return sources
    
    def get_full_context(self, content_id: str, content_type: str, collection_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full context for a specific piece of content using discussion builder.
        
        Args:
            content_id: Reddit ID of the content
            content_type: 'post' or 'comment'
            collection_id: Collection ID
        
        Returns:
            Full discussion context or None if not found
        """
        try:
            if content_type == 'post':
                discussion = discussion_builder.build_discussion_from_post(content_id, collection_id)
                return discussion.get('post') if discussion else None
            else:  # comment
                discussion = discussion_builder.build_discussion_from_comment(content_id, collection_id)
                # Return the specific comment data
                comments = discussion.get('comments', [])
                for comment in comments:
                    if comment.get('reddit_id') == content_id:
                        return comment
                return None
        except Exception:
            return None
    
    def get_available_search_types(self, collection_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get available search types and their status for given collections.
        
        Args:
            collection_ids: Collection IDs to check
        
        Returns:
            Dictionary with search type availability and requirements
        """
        from ..embeddings import vector_storage
        
        # Check indexing status
        embedding_stats = vector_storage.get_embedding_stats(collection_ids)
        has_local_embeddings = any(
            model_info['provider'] == 'local' 
            for model_info in embedding_stats.get('by_model', [])
        )
        has_cloud_embeddings = any(
            model_info['provider'] == 'openai' 
            for model_info in embedding_stats.get('by_model', [])
        )
        
        return {
            'keyword': {
                'available': True,
                'description': 'Keyword-based search with full discussion context',
                'requires_indexing': False,
                'cost': 'Free',
                'quality': 'Good for exact matches'
            },
            'local_semantic': {
                'available': has_local_embeddings,
                'description': 'Local semantic search with natural conversation understanding',
                'requires_indexing': True,
                'indexed': has_local_embeddings,
                'cost': 'Free (one-time indexing time)',
                'quality': 'Better for conceptual questions'
            },
            'cloud_semantic': {
                'available': has_cloud_embeddings,
                'description': 'Cloud semantic search with advanced understanding',
                'requires_indexing': True,
                'indexed': has_cloud_embeddings,
                'cost': 'Paid (OpenAI API tokens)',
                'quality': 'Best for complex conceptual questions'
            }
        }
    
    def get_representative_examples(self, collection_ids: List[str], 
                                  keywords: List[str], limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get representative discussion examples for summarization and analysis.
        
        Args:
            collection_ids: Collections to search in
            keywords: Keywords to find examples for
            limit: Maximum number of examples
        
        Returns:
            List of representative discussion contexts with natural formatting
        """
        try:
            # Get representative examples using discussion builder
            examples = discussion_builder.get_representative_examples(
                collection_ids, keywords, limit
            )
            
            # Format examples for LLM consumption
            formatted_examples = []
            for example in examples:
                formatted_text = content_formatter.format_discussion_thread(example)
                formatted_examples.append({
                    'discussion_data': example,
                    'formatted_text': formatted_text,
                    'post_title': example.get('post', {}).get('title', ''),
                    'subreddit': example.get('post', {}).get('subreddit', ''),
                    'comment_count': len(example.get('comments', []))
                })
            
            return formatted_examples
            
        except Exception as e:
            return []


# Global RAG engine instance
rag_engine = RAGEngine()
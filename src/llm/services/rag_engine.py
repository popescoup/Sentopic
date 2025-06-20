"""
RAG (Retrieval-Augmented Generation) Engine

Combines search results with LLM generation to answer questions about
analysis data. Supports multiple search modes and provides source attribution.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .search_engine import SearchEngineFactory, SearchResult
from ...llm import get_llm_provider
from ...database import db, Post, Comment  # ADDED db IMPORT


@dataclass
class RAGResponse:
    """Response from RAG engine with sources."""
    answer: str                     # AI-generated answer
    sources: List[Dict[str, Any]]   # Source attributions
    search_type: str               # Search method used
    search_results_count: int      # Number of search results found
    tokens_used: int               # LLM tokens used
    cost_estimate: float           # Cost estimate for this query


class RAGEngine:
    """
    RAG engine that combines search and generation.
    
    Takes user questions, searches for relevant content,
    and generates responses with source attribution.
    """
    
    def __init__(self):
        pass
    
    def answer_question(self, question: str, collection_ids: List[str], 
                       search_type: str = 'keyword', 
                       max_results: int = 5) -> RAGResponse:
        """
        Answer a question using RAG.
        
        Args:
            question: User's question
            collection_ids: Collection IDs to search in
            search_type: 'keyword', 'local_semantic', or 'cloud_semantic'
            max_results: Maximum search results to use
        
        Returns:
            RAGResponse with answer and sources
        """
        # Get search engine
        search_engine = SearchEngineFactory.create_engine(search_type)
        
        # Search for relevant content
        search_results = search_engine.search(question, collection_ids, limit=max_results)
        
        if not search_results:
            return RAGResponse(
                answer="I couldn't find any content in your data that relates to that question. Try rephrasing or asking about different topics covered in your analysis.",
                sources=[],
                search_type=search_type,
                search_results_count=0,
                tokens_used=0,
                cost_estimate=0.0
            )
        
        # Generate answer using LLM
        llm_response = self._generate_answer(question, search_results)
        
        # Format sources for attribution
        sources = self._format_sources(search_results)
        
        return RAGResponse(
            answer=llm_response['content'],
            sources=sources,
            search_type=search_type,
            search_results_count=len(search_results),
            tokens_used=llm_response['tokens_used'],
            cost_estimate=llm_response['cost_estimate']
        )
    
    def _generate_answer(self, question: str, search_results: List[SearchResult]) -> Dict[str, Any]:
        """Generate answer using LLM and search results."""
        # Get LLM provider
        provider = get_llm_provider()
        if not provider:
            raise RuntimeError("No LLM provider available. Please check your configuration.")
        
        # Build context from search results
        context = self._build_context(search_results)
        
        # Build prompts
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(question, context)
        
        # Generate response
        response = provider.generate(user_prompt, system_prompt)
        
        return {
            'content': response.content,
            'tokens_used': response.tokens_used,
            'cost_estimate': response.cost_estimate,
            'provider': response.provider,
            'model': response.model
        }
    
    def _build_context(self, search_results: List[SearchResult]) -> str:
        """Build context string from search results."""
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            # Format content with metadata
            content_type = "Post" if result.content_type == 'post' else "Comment"
            author = result.metadata.get('author', 'Unknown')
            score = result.metadata.get('score', 0)
            
            # Add title for posts
            title_info = ""
            if result.content_type == 'post' and result.metadata.get('title'):
                title_info = f" (Title: \"{result.metadata['title']}\")"
            
            # Format the context entry
            context_parts.append(f"""[Source {i}] {content_type} by {author} (Score: {score}){title_info}
ID: {result.content_id}
Content: {result.content_text[:500]}{"..." if len(result.content_text) > 500 else ""}
Relevance: {result.relevance_score:.3f}
""")
        
        return "\n".join(context_parts)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for RAG responses."""
        return """You are a helpful assistant that answers questions about Reddit discussion data. You have been provided with relevant posts and comments from Reddit collections.

Your responses should be:
- ACCURATE: Base your answers only on the provided source content
- SPECIFIC: Quote directly from sources when appropriate
- ATTRIBUTED: Reference source IDs when making claims
- HELPFUL: Organize information clearly and provide insights
- HONEST: If the sources don't contain enough information, say so

When quoting from sources:
- Use quotation marks for direct quotes
- Include the source ID in parentheses: (Source 1) or (Post ID: abc123)
- Multiple sources can support the same point

Format your response clearly with insights and specific examples from the data."""
    
    def _build_user_prompt(self, question: str, context: str) -> str:
        """Build user prompt with question and context."""
        return f"""Based on the Reddit discussion data provided below, please answer this question:

QUESTION: {question}

REDDIT DATA:
{context}

Please provide a comprehensive answer based on the sources above. Include specific quotes and reference the source IDs when making claims. If the question cannot be fully answered with the provided sources, please say so."""
    
    def _format_sources(self, search_results: List[SearchResult]) -> List[Dict[str, Any]]:
        """Format search results as source attributions."""
        sources = []
        
        for result in search_results:
            source = {
                'content_id': result.content_id,
                'content_type': result.content_type,
                'collection_id': result.collection_id,
                'relevance_score': result.relevance_score,
                'preview': result.content_text[:200] + "..." if len(result.content_text) > 200 else result.content_text,
                'author': result.metadata.get('author', 'Unknown'),
                'score': result.metadata.get('score', 0),
                'created_utc': result.metadata.get('created_utc')
            }
            
            # Add type-specific metadata
            if result.content_type == 'post':
                source['title'] = result.metadata.get('title', '')
                source['url'] = result.metadata.get('url', '')
            else:  # comment
                source['post_reddit_id'] = result.metadata.get('post_reddit_id', '')
                source['is_root'] = result.metadata.get('is_root', False)
            
            sources.append(source)
        
        return sources
    
    def get_full_context(self, content_id: str, content_type: str, collection_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full context for a specific piece of content.
        
        Args:
            content_id: Reddit ID of the content
            content_type: 'post' or 'comment'
            collection_id: Collection ID
        
        Returns:
            Full content details or None if not found
        """
        session = db.get_session()
        try:
            if content_type == 'post':
                post = session.query(Post).filter(
                    Post.reddit_id == content_id,
                    Post.collection_id == collection_id
                ).first()
                
                if post:
                    return {
                        'content_id': post.reddit_id,
                        'content_type': 'post',
                        'collection_id': post.collection_id,
                        'title': post.title,
                        'content': post.content or '',
                        'full_text': post.title + "\n\n" + (post.content or ''),
                        'author': post.author,
                        'score': post.score,
                        'upvote_ratio': post.upvote_ratio,
                        'created_utc': post.created_utc,
                        'url': post.url,
                        'is_self': post.is_self
                    }
            
            else:  # comment
                comment = session.query(Comment).filter(
                    Comment.reddit_id == content_id,
                    Comment.collection_id == collection_id
                ).first()
                
                if comment:
                    return {
                        'content_id': comment.reddit_id,
                        'content_type': 'comment',
                        'collection_id': comment.collection_id,
                        'content': comment.content,
                        'full_text': comment.content,
                        'author': comment.author,
                        'score': comment.score,
                        'created_utc': comment.created_utc,
                        'post_reddit_id': comment.post_reddit_id,
                        'parent_reddit_id': comment.parent_reddit_id,
                        'is_root': comment.is_root,
                        'depth': comment.depth,
                        'position': comment.position
                    }
            
            return None
            
        finally:
            session.close()
    
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
                'description': 'Keyword-based search (free, instant)',
                'requires_indexing': False,
                'cost': 'Free'
            },
            'local_semantic': {
                'available': has_local_embeddings,
                'description': 'Local semantic search (free, requires indexing)',
                'requires_indexing': True,
                'indexed': has_local_embeddings,
                'cost': 'Free (one-time indexing time)'
            },
            'cloud_semantic': {
                'available': has_cloud_embeddings,
                'description': 'Cloud semantic search (paid, higher quality)',
                'requires_indexing': True,
                'indexed': has_cloud_embeddings,
                'cost': 'Paid (OpenAI API tokens)'
            }
        }


# Global RAG engine instance
rag_engine = RAGEngine()
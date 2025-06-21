"""
Search Engine Service

Implements three-tier search system for RAG functionality with enhanced
context preservation and discussion-aware search results.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
from ...database import db, Post, Comment
from ..embeddings import vector_storage
from .. import get_embedding_provider
from .discussion_builder import discussion_builder


@dataclass
class SearchResult:
    """Enhanced search result with discussion context."""
    content_id: str          # Reddit ID of post/comment
    content_type: str        # 'post' or 'comment'
    collection_id: str       # Collection this content belongs to
    content_text: str        # Full text content
    relevance_score: float   # Search relevance (0.0 to 1.0)
    metadata: Dict[str, Any] # Enhanced metadata including discussion context
    discussion_context: Optional[Dict[str, Any]] = None  # Optional full discussion context


class SearchEngine(ABC):
    """Abstract base class for search engines with discussion awareness."""
    
    @abstractmethod
    def search(self, query: str, collection_ids: List[str], limit: int = 10) -> List[SearchResult]:
        """Search for content matching the query."""
        pass
    
    @abstractmethod
    def get_search_type(self) -> str:
        """Return the search type name."""
        pass
    
    @abstractmethod
    def requires_indexing(self) -> bool:
        """Return True if this search type requires content indexing."""
        pass
    
    def search_with_full_context(self, query: str, collection_ids: List[str], 
                                limit: int = 10) -> List[SearchResult]:
        """
        Search and automatically build full discussion contexts.
        
        Args:
            query: Search query
            collection_ids: Collections to search in
            limit: Maximum results to return
        
        Returns:
            Search results with full discussion contexts
        """
        # Get basic search results
        results = self.search(query, collection_ids, limit)
        
        # Enhance with full discussion contexts
        for result in results:
            if result.content_type == 'post':
                discussion = discussion_builder.build_discussion_from_post(
                    result.content_id, result.collection_id
                )
            else:  # comment
                discussion = discussion_builder.build_discussion_from_comment(
                    result.content_id, result.collection_id
                )
            
            result.discussion_context = discussion
        
        return results


class KeywordSearchEngine(SearchEngine):
    """
    Enhanced keyword-based search with better context preservation.
    """
    
    def search(self, query: str, collection_ids: List[str], limit: int = 10) -> List[SearchResult]:
        """Search using enhanced keyword matching with discussion context."""
        session = db.get_session()
        try:
            results = []
            
            # Prepare search terms
            search_terms = [term.strip().lower() for term in query.split() if term.strip()]
            if not search_terms:
                return results
            
            # Search in posts with enhanced metadata
            posts = session.query(Post).filter(
                Post.collection_id.in_(collection_ids)
            ).all()
            
            for post in posts:
                relevance = self._calculate_keyword_relevance(
                    post.title + " " + (post.content or ""), search_terms
                )
                if relevance > 0:
                    # Get enhanced metadata including comment count
                    comment_count = session.query(Comment).filter(
                        Comment.post_reddit_id == post.reddit_id,
                        Comment.collection_id == post.collection_id
                    ).count()
                    
                    results.append(SearchResult(
                        content_id=post.reddit_id,
                        content_type='post',
                        collection_id=post.collection_id,
                        content_text=post.title + "\n\n" + (post.content or ""),
                        relevance_score=relevance,
                        metadata={
                            'author': post.author,
                            'score': post.score,
                            'created_utc': post.created_utc,
                            'title': post.title,
                            'url': post.url,
                            'upvote_ratio': post.upvote_ratio,
                            'comment_count': comment_count,
                            'subreddit': post.subreddit
                        }
                    ))
            
            # Search in comments with enhanced context
            comments = session.query(Comment).filter(
                Comment.collection_id.in_(collection_ids)
            ).all()
            
            for comment in comments:
                relevance = self._calculate_keyword_relevance(comment.content, search_terms)
                if relevance > 0:
                    # Get parent post title for context
                    parent_post = session.query(Post).filter(
                        Post.reddit_id == comment.post_reddit_id,
                        Post.collection_id == comment.collection_id
                    ).first()
                    
                    parent_title = parent_post.title if parent_post else "Unknown Post"
                    
                    results.append(SearchResult(
                        content_id=comment.reddit_id,
                        content_type='comment',
                        collection_id=comment.collection_id,
                        content_text=comment.content,
                        relevance_score=relevance,
                        metadata={
                            'author': comment.author,
                            'score': comment.score,
                            'created_utc': comment.created_utc,
                            'post_reddit_id': comment.post_reddit_id,
                            'parent_post_title': parent_title,
                            'is_root': comment.is_root,
                            'depth': comment.depth,
                            'subreddit': parent_post.subreddit if parent_post else 'unknown'
                        }
                    ))
            
            # Sort by relevance and engagement
            results.sort(key=lambda x: (x.relevance_score, x.metadata.get('score', 0)), reverse=True)
            return results[:limit]
            
        finally:
            session.close()
    
    def _calculate_keyword_relevance(self, text: str, search_terms: List[str]) -> float:
        """Enhanced relevance calculation with context awareness."""
        if not text or not search_terms:
            return 0.0
        
        text_lower = text.lower()
        total_score = 0.0
        
        for term in search_terms:
            # Exact word matches (highest weight)
            word_pattern = r'\b' + re.escape(term) + r'\b'
            word_matches = len(re.findall(word_pattern, text_lower))
            
            # Partial matches (lower weight)
            partial_matches = text_lower.count(term) - word_matches
            
            # Position-based scoring (title/early content gets bonus)
            position_bonus = 1.0
            first_occurrence = text_lower.find(term)
            if first_occurrence != -1 and first_occurrence < 100:  # Early in content
                position_bonus = 1.5
            
            # Calculate term score
            term_score = (word_matches * 1.0 + partial_matches * 0.3) * position_bonus
            total_score += min(term_score, 2.0)  # Cap per term
        
        # Normalize by number of terms
        return min(total_score / len(search_terms), 1.0)
    
    def get_search_type(self) -> str:
        return "keyword"
    
    def requires_indexing(self) -> bool:
        return False


class LocalSemanticSearchEngine(SearchEngine):
    """
    Enhanced semantic search using local sentence-transformers with discussion context.
    """
    
    def search(self, query: str, collection_ids: List[str], limit: int = 10) -> List[SearchResult]:
        """Search using local semantic similarity with enhanced metadata."""
        if not self._is_content_indexed(collection_ids):
            raise RuntimeError("Content not indexed. Run indexing first with: python main.py --index-content <session_id>")
        
        # Generate query embedding
        from ..embeddings.providers import LocalEmbeddingProvider
        provider = LocalEmbeddingProvider({'model': 'all-MiniLM-L6-v2'})
        
        query_response = provider.generate_embeddings([query])
        if query_response.embeddings.size == 0:
            return []
        
        query_embedding = query_response.embeddings[0]
        
        # Search using vector storage
        vector_results = vector_storage.search_similar(
            query_embedding=query_embedding,
            collection_ids=collection_ids,
            limit=limit,
            min_similarity=0.3
        )
        
        # Convert to enhanced SearchResult format
        results = []
        session = db.get_session()
        try:
            for result in vector_results:
                metadata = self._get_enhanced_metadata(
                    result.content_id, result.content_type, result.collection_id, session
                )
                
                results.append(SearchResult(
                    content_id=result.content_id,
                    content_type=result.content_type,
                    collection_id=result.collection_id,
                    content_text=result.content_text,
                    relevance_score=result.similarity_score,
                    metadata=metadata
                ))
        finally:
            session.close()
        
        return results
    
    def _is_content_indexed(self, collection_ids: List[str]) -> bool:
        """Check if content is indexed with local embeddings."""
        stats = vector_storage.get_embedding_stats(collection_ids)
        for model_info in stats.get('by_model', []):
            if model_info.get('provider') == 'local':
                return model_info.get('count', 0) > 0
        return False
    
    def _get_enhanced_metadata(self, content_id: str, content_type: str, 
                             collection_id: str, session) -> Dict[str, Any]:
        """Get enhanced metadata including discussion context."""
        if content_type == 'post':
            post = session.query(Post).filter(
                Post.reddit_id == content_id,
                Post.collection_id == collection_id
            ).first()
            
            if post:
                comment_count = session.query(Comment).filter(
                    Comment.post_reddit_id == post.reddit_id,
                    Comment.collection_id == collection_id
                ).count()
                
                return {
                    'author': post.author,
                    'score': post.score,
                    'created_utc': post.created_utc,
                    'title': post.title,
                    'url': post.url,
                    'upvote_ratio': post.upvote_ratio,
                    'comment_count': comment_count,
                    'subreddit': post.subreddit
                }
        
        else:  # comment
            comment = session.query(Comment).filter(
                Comment.reddit_id == content_id,
                Comment.collection_id == collection_id
            ).first()
            
            if comment:
                # Get parent post for context
                parent_post = session.query(Post).filter(
                    Post.reddit_id == comment.post_reddit_id,
                    Post.collection_id == collection_id
                ).first()
                
                return {
                    'author': comment.author,
                    'score': comment.score,
                    'created_utc': comment.created_utc,
                    'post_reddit_id': comment.post_reddit_id,
                    'parent_post_title': parent_post.title if parent_post else 'Unknown Post',
                    'is_root': comment.is_root,
                    'depth': comment.depth,
                    'subreddit': parent_post.subreddit if parent_post else 'unknown'
                }
        
        return {}
    
    def get_search_type(self) -> str:
        return "local_semantic"
    
    def requires_indexing(self) -> bool:
        return True


class CloudSemanticSearchEngine(SearchEngine):
    """
    Enhanced semantic search using cloud embeddings (OpenAI) with discussion context.
    """
    
    def search(self, query: str, collection_ids: List[str], limit: int = 10) -> List[SearchResult]:
        """Search using cloud semantic similarity with enhanced metadata."""
        if not self._is_content_indexed_cloud(collection_ids):
            raise RuntimeError("Content not indexed with cloud embeddings. Run cloud indexing first.")
        
        # Get OpenAI embedding provider
        provider = get_embedding_provider()
        if not provider or provider.get_provider_name() != 'openai_embeddings':
            raise RuntimeError("OpenAI embeddings not available. Check configuration.")
        
        # Generate query embedding
        query_response = provider.generate_embeddings([query])
        if query_response.embeddings.size == 0:
            return []
        
        query_embedding = query_response.embeddings[0]
        
        # Search using vector storage
        vector_results = vector_storage.search_similar(
            query_embedding=query_embedding,
            collection_ids=collection_ids,
            limit=limit,
            min_similarity=0.4
        )
        
        # Convert to enhanced SearchResult format
        results = []
        session = db.get_session()
        try:
            for result in vector_results:
                metadata = self._get_enhanced_metadata(
                    result.content_id, result.content_type, result.collection_id, session
                )
                
                results.append(SearchResult(
                    content_id=result.content_id,
                    content_type=result.content_type,
                    collection_id=result.collection_id,
                    content_text=result.content_text,
                    relevance_score=result.similarity_score,
                    metadata=metadata
                ))
        finally:
            session.close()
        
        return results
    
    def _is_content_indexed_cloud(self, collection_ids: List[str]) -> bool:
        """Check if content is indexed with cloud embeddings."""
        session = db.get_session()
        try:
            from ...database import ContentEmbedding
            result = session.query(ContentEmbedding).filter(
                ContentEmbedding.collection_id.in_(collection_ids),
                ContentEmbedding.provider == 'openai'
            ).first()
            return result is not None
        finally:
            session.close()
    
    def _get_enhanced_metadata(self, content_id: str, content_type: str, 
                             collection_id: str, session) -> Dict[str, Any]:
        """Get enhanced metadata including discussion context."""
        # Same implementation as LocalSemanticSearchEngine
        if content_type == 'post':
            post = session.query(Post).filter(
                Post.reddit_id == content_id,
                Post.collection_id == collection_id
            ).first()
            
            if post:
                comment_count = session.query(Comment).filter(
                    Comment.post_reddit_id == post.reddit_id,
                    Comment.collection_id == collection_id
                ).count()
                
                return {
                    'author': post.author,
                    'score': post.score,
                    'created_utc': post.created_utc,
                    'title': post.title,
                    'url': post.url,
                    'upvote_ratio': post.upvote_ratio,
                    'comment_count': comment_count,
                    'subreddit': post.subreddit
                }
        
        else:  # comment
            comment = session.query(Comment).filter(
                Comment.reddit_id == content_id,
                Comment.collection_id == collection_id
            ).first()
            
            if comment:
                # Get parent post for context
                parent_post = session.query(Post).filter(
                    Post.reddit_id == comment.post_reddit_id,
                    Post.collection_id == collection_id
                ).first()
                
                return {
                    'author': comment.author,
                    'score': comment.score,
                    'created_utc': comment.created_utc,
                    'post_reddit_id': comment.post_reddit_id,
                    'parent_post_title': parent_post.title if parent_post else 'Unknown Post',
                    'is_root': comment.is_root,
                    'depth': comment.depth,
                    'subreddit': parent_post.subreddit if parent_post else 'unknown'
                }
        
        return {}
    
    def get_search_type(self) -> str:
        return "cloud_semantic"
    
    def requires_indexing(self) -> bool:
        return True


class SearchEngineFactory:
    """Enhanced factory for creating search engines."""
    
    ENGINES = {
        'keyword': KeywordSearchEngine,
        'local_semantic': LocalSemanticSearchEngine,
        'cloud_semantic': CloudSemanticSearchEngine
    }
    
    @classmethod
    def create_engine(cls, search_type: str) -> SearchEngine:
        """Create a search engine of the specified type."""
        if search_type not in cls.ENGINES:
            available = list(cls.ENGINES.keys())
            raise ValueError(f"Unknown search type '{search_type}'. Available: {available}")
        
        engine_class = cls.ENGINES[search_type]
        return engine_class()
    
    @classmethod
    def get_available_engines(cls) -> List[str]:
        """Get list of available search engine types."""
        return list(cls.ENGINES.keys())
    
    @classmethod
    def search_with_best_available(cls, query: str, collection_ids: List[str], 
                                  limit: int = 10) -> List[SearchResult]:
        """
        Search using the best available search method.
        
        Tries semantic search first, falls back to keyword search.
        """
        # Try cloud semantic first
        try:
            engine = cls.create_engine('cloud_semantic')
            return engine.search_with_full_context(query, collection_ids, limit)
        except RuntimeError:
            pass
        
        # Try local semantic
        try:
            engine = cls.create_engine('local_semantic')
            return engine.search_with_full_context(query, collection_ids, limit)
        except RuntimeError:
            pass
        
        # Fall back to keyword search
        engine = cls.create_engine('keyword')
        return engine.search_with_full_context(query, collection_ids, limit)
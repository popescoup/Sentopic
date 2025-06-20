"""
Search Engine Service

Implements three-tier search system for RAG functionality:
1. Keyword Search (free, instant)
2. Local Semantic Search (free, requires indexing) 
3. Cloud Semantic Search (paid, higher quality)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
from ...database import db, Post, Comment
from ..embeddings import vector_storage, get_embedding_provider


@dataclass
class SearchResult:
    """Result from content search."""
    content_id: str          # Reddit ID of post/comment
    content_type: str        # 'post' or 'comment'
    collection_id: str       # Collection this content belongs to
    content_text: str        # Full text content
    relevance_score: float   # Search relevance (0.0 to 1.0)
    metadata: Dict[str, Any] # Additional metadata (author, score, date, etc.)


class SearchEngine(ABC):
    """Abstract base class for search engines."""
    
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


class KeywordSearchEngine(SearchEngine):
    """
    Keyword-based search using SQL text search.
    Free and instant, good for exact matches.
    """
    
    def search(self, query: str, collection_ids: List[str], limit: int = 10) -> List[SearchResult]:
        """Search using keyword matching."""
        session = db.get_session()
        try:
            results = []
            
            # Prepare search terms (split query into keywords)
            search_terms = [term.strip().lower() for term in query.split() if term.strip()]
            if not search_terms:
                return results
            
            # Search in posts
            posts = session.query(Post).filter(
                Post.collection_id.in_(collection_ids)
            ).all()
            
            for post in posts:
                relevance = self._calculate_keyword_relevance(
                    post.title + " " + (post.content or ""), search_terms
                )
                if relevance > 0:
                    results.append(SearchResult(
                        content_id=post.reddit_id,
                        content_type='post',
                        collection_id=post.collection_id,
                        content_text=post.title + " " + (post.content or ""),
                        relevance_score=relevance,
                        metadata={
                            'author': post.author,
                            'score': post.score,
                            'created_utc': post.created_utc,
                            'title': post.title,
                            'url': post.url
                        }
                    ))
            
            # Search in comments
            comments = session.query(Comment).filter(
                Comment.collection_id.in_(collection_ids)
            ).all()
            
            for comment in comments:
                relevance = self._calculate_keyword_relevance(comment.content, search_terms)
                if relevance > 0:
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
                            'is_root': comment.is_root
                        }
                    ))
            
            # Sort by relevance and limit
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            return results[:limit]
            
        finally:
            session.close()
    
    def _calculate_keyword_relevance(self, text: str, search_terms: List[str]) -> float:
        """Calculate relevance score based on keyword matches."""
        if not text or not search_terms:
            return 0.0
        
        text_lower = text.lower()
        matches = 0
        total_terms = len(search_terms)
        
        for term in search_terms:
            # Count exact word matches
            word_pattern = r'\b' + re.escape(term) + r'\b'
            word_matches = len(re.findall(word_pattern, text_lower))
            
            # Count partial matches (lower weight)
            partial_matches = text_lower.count(term) - word_matches
            
            # Calculate term score
            term_score = word_matches + (partial_matches * 0.5)
            matches += min(term_score, 1.0)  # Cap at 1.0 per term
        
        return matches / total_terms
    
    def get_search_type(self) -> str:
        return "keyword"
    
    def requires_indexing(self) -> bool:
        return False


class LocalSemanticSearchEngine(SearchEngine):
    """
    Semantic search using local sentence-transformers.
    Free but requires one-time indexing.
    """
    
    def search(self, query: str, collection_ids: List[str], limit: int = 10) -> List[SearchResult]:
        """Search using local semantic similarity."""
        # Check if content is indexed
        if not self._is_content_indexed(collection_ids):
            raise RuntimeError("Content not indexed. Run indexing first with: python main.py --index-content <session_id>")
        
        # Get local embedding provider
        from ..embeddings.providers import LocalEmbeddingProvider
        provider = LocalEmbeddingProvider({'model': 'all-MiniLM-L6-v2'})
        
        # Generate query embedding
        query_response = provider.generate_embeddings([query])
        if query_response.embeddings.size == 0:
            return []
        
        query_embedding = query_response.embeddings[0]
        
        # Search using vector storage
        search_results = vector_storage.search_similar(
            query_embedding=query_embedding,
            collection_ids=collection_ids,
            limit=limit,
            min_similarity=0.3  # Minimum similarity threshold
        )
        
        # Convert to SearchResult format
        results = []
        for result in search_results:
            # Get additional metadata
            metadata = self._get_content_metadata(result.content_id, result.content_type, result.collection_id)
            
            results.append(SearchResult(
                content_id=result.content_id,
                content_type=result.content_type,
                collection_id=result.collection_id,
                content_text=result.content_text,
                relevance_score=result.similarity_score,
                metadata=metadata
            ))
        
        return results
    
    def _is_content_indexed(self, collection_ids: List[str]) -> bool:
        """Check if content for these collections is indexed."""
        stats = vector_storage.get_embedding_stats(collection_ids)
        return stats['total_embeddings'] > 0
    
    def _get_content_metadata(self, content_id: str, content_type: str, collection_id: str) -> Dict[str, Any]:
        """Get metadata for content."""
        session = db.get_session()
        try:
            if content_type == 'post':
                post = session.query(Post).filter(
                    Post.reddit_id == content_id,
                    Post.collection_id == collection_id
                ).first()
                if post:
                    return {
                        'author': post.author,
                        'score': post.score,
                        'created_utc': post.created_utc,
                        'title': post.title,
                        'url': post.url
                    }
            else:  # comment
                comment = session.query(Comment).filter(
                    Comment.reddit_id == content_id,
                    Comment.collection_id == collection_id
                ).first()
                if comment:
                    return {
                        'author': comment.author,
                        'score': comment.score,
                        'created_utc': comment.created_utc,
                        'post_reddit_id': comment.post_reddit_id,
                        'is_root': comment.is_root
                    }
            return {}
        finally:
            session.close()
    
    def get_search_type(self) -> str:
        return "local_semantic"
    
    def requires_indexing(self) -> bool:
        return True


class CloudSemanticSearchEngine(SearchEngine):
    """
    Semantic search using cloud embeddings (OpenAI).
    Higher quality but costs API tokens.
    """
    
    def search(self, query: str, collection_ids: List[str], limit: int = 10) -> List[SearchResult]:
        """Search using cloud semantic similarity."""
        # Check if content is indexed with cloud embeddings
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
        search_results = vector_storage.search_similar(
            query_embedding=query_embedding,
            collection_ids=collection_ids,
            limit=limit,
            min_similarity=0.4  # Higher threshold for cloud embeddings
        )
        
        # Convert to SearchResult format
        results = []
        for result in search_results:
            # Get additional metadata
            metadata = self._get_content_metadata(result.content_id, result.content_type, result.collection_id)
            
            results.append(SearchResult(
                content_id=result.content_id,
                content_type=result.content_type,
                collection_id=result.collection_id,
                content_text=result.content_text,
                relevance_score=result.similarity_score,
                metadata=metadata
            ))
        
        return results
    
    def _is_content_indexed_cloud(self, collection_ids: List[str]) -> bool:
        """Check if content is indexed with cloud embeddings."""
        # Check if any embeddings exist with OpenAI provider
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
    
    def _get_content_metadata(self, content_id: str, content_type: str, collection_id: str) -> Dict[str, Any]:
        """Get metadata for content."""
        session = db.get_session()
        try:
            if content_type == 'post':
                post = session.query(Post).filter(
                    Post.reddit_id == content_id,
                    Post.collection_id == collection_id
                ).first()
                if post:
                    return {
                        'author': post.author,
                        'score': post.score,
                        'created_utc': post.created_utc,
                        'title': post.title,
                        'url': post.url
                    }
            else:  # comment
                comment = session.query(Comment).filter(
                    Comment.reddit_id == content_id,
                    Comment.collection_id == collection_id
                ).first()
                if comment:
                    return {
                        'author': comment.author,
                        'score': comment.score,
                        'created_utc': comment.created_utc,
                        'post_reddit_id': comment.post_reddit_id,
                        'is_root': comment.is_root
                    }
            return {}
        finally:
            session.close()
    
    def get_search_type(self) -> str:
        return "cloud_semantic"
    
    def requires_indexing(self) -> bool:
        return True


class SearchEngineFactory:
    """Factory for creating search engines."""
    
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
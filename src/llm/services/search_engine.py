"""
Search Engine Service

Enhanced search system with analytics-driven search capabilities alongside
traditional keyword and semantic search methods.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
from ...database import db, Post, Comment
from ..embeddings import vector_storage
from .. import get_embedding_provider
from .discussion_builder import discussion_builder
from .analytics_search_engine import analytics_search_engine, AnalyticsSearchResult
import numpy as np

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
    analytics_context: Optional[Dict[str, Any]] = None   # Optional analytics insights


class SearchEngine(ABC):
    """Abstract base class for search engines with discussion and analytics awareness."""
    
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


class AnalyticsDrivenSearchEngine(SearchEngine):
    """
    NEW: Analytics-driven search engine that uses your existing keyword analysis
    data to find precise, contextually relevant discussions.
    """
    
    def search(self, query: str, collection_ids: List[str], limit: int = 10) -> List[SearchResult]:
        """Search using analytics data to find precise keyword occurrences."""
        # Extract keywords from query - could be enhanced with more sophisticated NLP
        potential_keywords = self._extract_keywords_from_query(query)
        
        results = []
        
        # Get available keywords from analytics
        available_keywords = self._get_available_keywords(collection_ids)
        
        # Find matching keywords
        matching_keywords = []
        for keyword in potential_keywords:
            for available_keyword in available_keywords:
                if keyword.lower() in available_keyword.lower() or available_keyword.lower() in keyword.lower():
                    matching_keywords.append(available_keyword)
        
        # If no keyword matches, try to find the most relevant keywords based on query intent
        if not matching_keywords:
            matching_keywords = self._find_contextually_relevant_keywords(query, available_keywords)
        
        # Get analytics-driven results for matching keywords
        for keyword in matching_keywords[:3]:  # Limit to top 3 keywords to avoid overwhelming results
            analytics_results = analytics_search_engine.search_by_keyword_analytics(
                keyword, collection_ids, limit=limit // len(matching_keywords) + 1
            )
            
            # Convert analytics results to standard SearchResult format
            for analytics_result in analytics_results:
                search_result = self._convert_analytics_to_search_result(analytics_result, query)
                results.append(search_result)
        
        # Sort by relevance (combination of analytics relevance and query matching)
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results[:limit]
    
    def _extract_keywords_from_query(self, query: str) -> List[str]:
        """Extract potential keywords from user query."""
        # Remove common question words and focus on content words
        stop_words = {
            'what', 'why', 'how', 'when', 'where', 'who', 'which', 'that', 'this',
            'are', 'is', 'was', 'were', 'do', 'does', 'did', 'can', 'could', 'should',
            'would', 'will', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'about', 'people', 'users', 'discussions', 'comments',
            'posts', 'say', 'think', 'feel', 'mention', 'talk', 'discuss'
        }
        
        # Extract quoted terms first
        quoted_terms = re.findall(r'"([^"]*)"', query)
        
        # Extract other words
        words = re.findall(r'\b[a-zA-Z]{2,}\b', query.lower())
        content_words = [w for w in words if w not in stop_words]
        
        # Combine quoted terms and content words
        keywords = quoted_terms + content_words
        
        return list(set(keywords))  # Remove duplicates
    
    def _get_available_keywords(self, collection_ids: List[str]) -> List[str]:
        """Get list of keywords available in analytics data."""
        session = db.get_session()
        try:
            from ...database import KeywordStat, AnalysisSession
            import json
        
            # FIXED: Get analysis sessions that analyzed these collections
            analysis_sessions = session.query(AnalysisSession).all()
        
            matching_session_ids = []
            for analysis_session in analysis_sessions:
                session_collection_ids = json.loads(analysis_session.collection_ids)
                if any(collection_id in session_collection_ids for collection_id in collection_ids):
                    matching_session_ids.append(analysis_session.id)
        
            if not matching_session_ids:
                return []
        
            keywords = session.query(KeywordStat.keyword).filter(
                KeywordStat.analysis_session_id.in_(matching_session_ids)  # FIXED: Use analysis_session_id
            ).distinct().all()
            return [kw.keyword for kw in keywords]
        except:
            return []
        finally:
            session.close()
    
    def _find_contextually_relevant_keywords(self, query: str, available_keywords: List[str]) -> List[str]:
        """Find keywords that might be contextually relevant to the query."""
        query_lower = query.lower()
        relevant_keywords = []
        
        # Look for partial matches or related terms
        for keyword in available_keywords:
            keyword_lower = keyword.lower()
            
            # Direct substring match
            if keyword_lower in query_lower or any(word in keyword_lower for word in query_lower.split()):
                relevant_keywords.append(keyword)
            
            # If query mentions frequency/statistics, include top keywords
            elif any(term in query_lower for term in ['frequent', 'often', 'most', 'top', 'popular']):
                # This would be handled by getting top keywords by frequency
                pass
        
        # If still no matches and query seems to be asking about frequency/stats, get top keywords
        if not relevant_keywords and any(term in query_lower for term in ['frequent', 'often', 'most', 'common', 'popular', 'top']):
            # Get top 3 most frequent keywords
            try:
                top_keywords_results = analytics_search_engine.search_by_analytics_insights(
                    available_keywords[:1] if available_keywords else [],  # Use first collection as proxy
                    'most_frequent', 
                    limit=3
                )
                relevant_keywords = [result.keyword for result in top_keywords_results]
            except:
                relevant_keywords = available_keywords[:3]  # Fallback to first 3
        
        return relevant_keywords[:5]  # Limit to prevent overwhelming results
    
    def _convert_analytics_to_search_result(self, analytics_result: AnalyticsSearchResult, 
                                          original_query: str) -> SearchResult:
        """Convert analytics search result to standard search result format."""
        # Calculate relevance based on analytics data and query matching
        relevance_score = self._calculate_analytics_relevance(analytics_result, original_query)
        
        return SearchResult(
            content_id=analytics_result.content_id,
            content_type=analytics_result.content_type,
            collection_id=analytics_result.collection_id,
            content_text=analytics_result.mention_context,
            relevance_score=relevance_score,
            metadata=analytics_result.analytics_metadata,
            analytics_context={
                'keyword': analytics_result.keyword,
                'sentiment_score': analytics_result.sentiment_score,
                'analytics_metadata': analytics_result.analytics_metadata
            }
        )
    
    def _calculate_analytics_relevance(self, analytics_result: AnalyticsSearchResult, 
                                     original_query: str) -> float:
        """Calculate relevance score for analytics-driven results."""
        score = 0.0
        
        # Base score from sentiment (higher sentiment = higher relevance for positive queries)
        sentiment_bonus = max(0, analytics_result.sentiment_score) * 0.3
        
        # Keyword frequency bonus
        if analytics_result.analytics_metadata.get('keyword_frequency_rank'):
            rank = analytics_result.analytics_metadata['keyword_frequency_rank']
            frequency_bonus = max(0, (10 - rank) / 10) * 0.4  # Higher rank = higher bonus
        else:
            frequency_bonus = 0.2  # Default bonus
        
        # Query matching bonus
        query_lower = original_query.lower()
        keyword_lower = analytics_result.keyword.lower()
        if keyword_lower in query_lower:
            query_bonus = 0.3
        else:
            query_bonus = 0.1
        
        score = sentiment_bonus + frequency_bonus + query_bonus
        return min(score, 1.0)  # Cap at 1.0
    
    def get_search_type(self) -> str:
        return "analytics_driven"
    
    def requires_indexing(self) -> bool:
        return False  # Uses existing analytics data


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
        if not provider or provider.get_provider_name() != 'openai':
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
    """Enhanced factory for creating search engines with analytics support."""
    
    ENGINES = {
        'keyword': KeywordSearchEngine,
        'local_semantic': LocalSemanticSearchEngine,
        'cloud_semantic': CloudSemanticSearchEngine,
        'analytics_driven': AnalyticsDrivenSearchEngine  # NEW
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
                                  limit: int = 10, prefer_analytics: bool = True) -> List[SearchResult]:
        """
        Search using the best available search method with analytics preference.
        
        Args:
            query: Search query
            collection_ids: Collections to search in
            limit: Maximum results to return
            prefer_analytics: If True, try analytics-driven search first
        
        Returns:
            Search results using the best available method
        """
        # Try analytics-driven search first if preferred and available
        if prefer_analytics:
            try:
                engine = cls.create_engine('analytics_driven')
                results = engine.search_with_full_context(query, collection_ids, limit)
                if results:  # If we got results, return them
                    return results
            except Exception:
                pass  # Fall through to other methods
        
        # Try cloud semantic search
        try:
            engine = cls.create_engine('cloud_semantic')
            return engine.search_with_full_context(query, collection_ids, limit)
        except RuntimeError:
            pass
        
        # Try local semantic search
        try:
            engine = cls.create_engine('local_semantic')
            return engine.search_with_full_context(query, collection_ids, limit)
        except RuntimeError:
            pass
        
        # Fall back to keyword search
        engine = cls.create_engine('keyword')
        return engine.search_with_full_context(query, collection_ids, limit)
    
    @classmethod
    def get_search_capabilities(cls, collection_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get comprehensive search capabilities for given collections.
        
        Args:
            collection_ids: Collection IDs to check capabilities for
        
        Returns:
            Dictionary with detailed search capabilities
        """
        capabilities = {}
        
        # Check each search engine type
        for engine_name, engine_class in cls.ENGINES.items():
            try:
                engine = engine_class()
                
                # Basic availability
                capabilities[engine_name] = {
                    'available': True,
                    'requires_indexing': engine.requires_indexing(),
                    'engine_type': engine.get_search_type()
                }
                
                # Check specific requirements
                if engine_name == 'analytics_driven':
                    # Check if analytics data is available
                    analytics_engine = AnalyticsDrivenSearchEngine()
                    available_keywords = analytics_engine._get_available_keywords(collection_ids)
                    capabilities[engine_name].update({
                        'analytics_keywords_available': len(available_keywords),
                        'sample_keywords': available_keywords[:5],
                        'description': 'Uses your keyword analysis data for precise results'
                    })
                
                elif engine_name in ['local_semantic', 'cloud_semantic']:
                    # Check indexing status
                    from ..embeddings import vector_storage
                    embedding_stats = vector_storage.get_embedding_stats(collection_ids)
                    
                    provider_type = 'local' if engine_name == 'local_semantic' else 'openai'
                    indexed = any(
                        model_info['provider'] == provider_type
                        for model_info in embedding_stats.get('by_model', [])
                    )
                    
                    capabilities[engine_name].update({
                        'indexed': indexed,
                        'total_embeddings': embedding_stats.get('total_embeddings', 0),
                        'description': f'Semantic search using {provider_type} embeddings'
                    })
                
                else:  # keyword
                    capabilities[engine_name].update({
                        'description': 'Traditional keyword-based search with enhanced context'
                    })
                    
            except Exception as e:
                capabilities[engine_name] = {
                    'available': False,
                    'error': str(e),
                    'description': f'Search engine {engine_name} is not available'
                }
        
        return capabilities
"""
Content Indexing Service

Handles generation and storage of embeddings for semantic search.
Supports both local (free) and cloud (paid) embedding providers.
"""

from typing import List, Dict, Any, Optional
from tqdm import tqdm
import json

from ...database import db, Post, Comment
from .providers import EmbeddingProviderFactory
from .storage import vector_storage


class ContentIndexer:
    """
    Service for indexing Reddit content with embeddings.
    
    Generates vector embeddings for posts and comments to enable
    semantic search capabilities.
    """
    
    def __init__(self):
        self.batch_size = 50  # Process content in batches
    
    def index_analysis_content(self, analysis_session_id: str, 
                              provider_type: str = 'local',
                              force_reindex: bool = False) -> Dict[str, Any]:
        """
        Index all content from an analysis session.
        
        Args:
            analysis_session_id: Analysis session to index
            provider_type: 'local' or 'openai'
            force_reindex: If True, reindex even if already indexed
        
        Returns:
            Dictionary with indexing results
        """
        # Get analysis session
        analysis_session = db.get_analysis_session(analysis_session_id)
        if not analysis_session:
            raise ValueError(f"Analysis session not found: {analysis_session_id}")
        
        collection_ids = json.loads(analysis_session.collection_ids)

        posts, comments = self._get_collection_content(collection_ids)
        total_content = len(posts) + len(comments)
        
        # Check if already indexed
        if not force_reindex:
            existing_count = self._get_existing_embeddings_count(collection_ids, provider_type)
            total_content = len(posts) + len(comments)  # We calculate this just below anyway
            if existing_count >= total_content and total_content > 0:  # ← FIX: All content indexed = skip
                return {
                    'status': 'already_indexed',
                    'message': f'Content already indexed with {provider_type} provider ({existing_count}/{total_content} embeddings exist)',
                    'embeddings_generated': 0,
                    'cost_estimate': 0.0
                }
        
        total_content_items = len(posts) + len(comments)
        if total_content_items == 0:
            return {
                'status': 'no_content',
                'message': 'No content found to index',
                'embeddings_generated': 0,
                'cost_estimate': 0.0
            }
        
        print(f"🔍 Indexing {total_content_items} items with {provider_type} embeddings...")
        print(f"   Posts: {len(posts)}, Comments: {len(comments)}")
        
        # Create embedding provider
        provider_config = self._get_provider_config(provider_type)
        provider = EmbeddingProviderFactory.create_provider(provider_config)
        
        # Index content
        total_embeddings = 0
        total_cost = 0.0
        
        # Index posts
        if posts:
            print("\n📝 Processing posts...")
            post_results = self._index_content_batch(posts, provider, 'post')
            total_embeddings += post_results['embeddings_generated']
            total_cost += post_results['cost_estimate']
        
        # Index comments
        if comments:
            print("\n💬 Processing comments...")
            comment_results = self._index_content_batch(comments, provider, 'comment')
            total_embeddings += comment_results['embeddings_generated']
            total_cost += comment_results['cost_estimate']
        
        print(f"\n✅ Indexing completed!")
        print(f"   Embeddings generated: {total_embeddings}")
        if total_cost > 0:
            print(f"   Estimated cost: ${total_cost:.4f}")
        
        return {
            'status': 'completed',
            'message': f'Successfully indexed {total_embeddings} items',
            'embeddings_generated': total_embeddings,
            'cost_estimate': total_cost,
            'provider_type': provider_type
        }
    
    def _get_collection_content(self, collection_ids: List[str]) -> tuple:
        """Get all posts and comments from collections."""
        session = db.get_session()
        try:
            # Get all posts
            posts = session.query(Post).filter(
                Post.collection_id.in_(collection_ids)
            ).all()
            
            # Get all comments
            comments = session.query(Comment).filter(
                Comment.collection_id.in_(collection_ids)
            ).all()
            
            # Convert to content items format
            post_items = []
            for post in posts:
                # Combine title and content for posts
                content_text = post.title
                if post.content:
                    content_text += "\n\n" + post.content
                
                post_items.append({
                    'content_id': post.reddit_id,
                    'content_type': 'post',
                    'collection_id': post.collection_id,
                    'text': content_text
                })
            
            comment_items = []
            for comment in comments:
                comment_items.append({
                    'content_id': comment.reddit_id,
                    'content_type': 'comment',
                    'collection_id': comment.collection_id,
                    'text': comment.content
                })
            
            return post_items, comment_items
            
        finally:
            session.close()
    
    def _index_content_batch(self, content_items: List[Dict[str, Any]], 
                           provider, content_type: str) -> Dict[str, Any]:
        """Index a batch of content items."""
        total_processed = 0
        total_cost = 0.0
        
        # Process in batches
        with tqdm(total=len(content_items), desc=f"Indexing {content_type}s", unit="item") as pbar:
            for i in range(0, len(content_items), self.batch_size):
                batch = content_items[i:i + self.batch_size]
                
                # Extract texts for embedding generation
                texts = [item['text'] for item in batch]
                
                # Generate embeddings
                response = provider.generate_embeddings(texts)
                
                if response.embeddings.size > 0:
                    # Store embeddings
                    vector_storage.store_embeddings(
                        content_items=batch,
                        embeddings=response.embeddings,
                        model=response.model,
                        provider=response.provider
                    )
                    
                    total_processed += len(batch)
                    total_cost += response.cost_estimate
                
                pbar.update(len(batch))
        
        return {
            'embeddings_generated': total_processed,
            'cost_estimate': total_cost
        }
    
    def _get_provider_config(self, provider_type: str) -> Dict[str, Any]:
        """Get configuration for embedding provider."""
        if provider_type == 'local':
            return {
                'provider': 'local',
                'model': 'all-MiniLM-L6-v2'  # Good balance of speed and quality
            }
        elif provider_type == 'openai':
            # Get OpenAI config from LLM configuration
            from ...llm.config import llm_config
            
            if not llm_config.is_enabled():
                raise RuntimeError("LLM not enabled. Cannot use OpenAI embeddings.")
            
            openai_config = llm_config.get_provider_config('openai')
            if not openai_config or not openai_config.get('api_key'):
                raise RuntimeError("OpenAI not configured. Cannot use OpenAI embeddings.")
            
            embeddings_config = llm_config.get_embeddings_config()
            
            return {
                'provider': 'openai',
                'model': embeddings_config.get('model', 'text-embedding-3-small'),
                'api_key': openai_config['api_key']
            }
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    def _get_existing_embeddings_count(self, collection_ids: List[str], provider_type: str) -> int:
        """Check if content is already indexed."""
        stats = vector_storage.get_embedding_stats(collection_ids)
        
        provider_name = 'local' if provider_type == 'local' else 'openai'
        
        for model_info in stats.get('by_model', []):
            if model_info.get('provider') == provider_name:
                return model_info.get('count', 0)
        
        return 0
    
    def get_indexing_status(self, analysis_session_id: str) -> Dict[str, Any]:
        """
        Get indexing status for an analysis session.
    
        Args:
            analysis_session_id: Analysis session ID
    
        Returns:
            Dictionary with indexing status
        """
        # Get analysis session
        analysis_session = db.get_analysis_session(analysis_session_id)
        if not analysis_session:
            raise ValueError(f"Analysis session not found: {analysis_session_id}")
    
        collection_ids = json.loads(analysis_session.collection_ids)
    
        # Get embedding statistics
        stats = vector_storage.get_embedding_stats(collection_ids)
    
        # Count content items
        session = db.get_session()
        try:
            total_posts = session.query(Post).filter(
                Post.collection_id.in_(collection_ids)
            ).count()
        
            total_comments = session.query(Comment).filter(
                Comment.collection_id.in_(collection_ids)
            ).count()
        
            total_content = total_posts + total_comments
        
        finally:
            session.close()
    
        # Analyze indexing status
        local_indexed = 0
        cloud_indexed = 0
    
        for model_info in stats.get('by_model', []):
            if model_info.get('provider') == 'local':
                local_indexed = model_info.get('count', 0)
            elif model_info.get('provider') == 'openai':
                cloud_indexed = model_info.get('count', 0)
    
        # ADD DEBUG LOGGING HERE
        print(f"🔍 FINAL STATUS CALCULATION FOR PROJECT: {analysis_session_id}")
        print(f"   Collections: {collection_ids}")
        print(f"   Total content: {total_content}")
        print(f"   Local indexed: {local_indexed}")  
        print(f"   Cloud indexed: {cloud_indexed}")
        print(f"   Raw embedding stats: {stats}")
    
        # Calculate status
        local_status = 'complete' if local_indexed >= total_content else 'partial' if local_indexed > 0 else 'none'
        cloud_status = 'complete' if cloud_indexed >= total_content else 'partial' if cloud_indexed > 0 else 'none'
    
        print(f"   Calculated local status: {local_status}")
        print(f"   Calculated cloud status: {cloud_status}")
    
        search_capabilities = {
            'keyword': True,
            'local_semantic': local_status == 'complete',  # ← FIX: Only if complete
            'cloud_semantic': cloud_status == 'complete'   # ← FIX: Only if complete
        }
    
        print(f"   Search capabilities: {search_capabilities}")
    
        result = {
            'total_content_items': total_content,
            'total_posts': total_posts,
            'total_comments': total_comments,
            'total_embeddings': stats['total_embeddings'],
            'local_indexed': local_indexed,
            'cloud_indexed': cloud_indexed,
            'indexing_status': {
                'local': local_status,
                'cloud': cloud_status
            },
            'search_capabilities': {
                'keyword': True,
                'local_semantic': local_indexed > 0,
                'cloud_semantic': cloud_indexed > 0
            }
        }
    
        print(f"   Final API response: {result}")
        print("🔍 END STATUS CALCULATION")
    
        return result
    
    def delete_embeddings(self, analysis_session_id: str, provider_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete embeddings for an analysis session.
        
        Args:
            analysis_session_id: Analysis session ID
            provider_type: 'local', 'openai', or None for all
        
        Returns:
            Dictionary with deletion results
        """
        # Get analysis session
        analysis_session = db.get_analysis_session(analysis_session_id)
        if not analysis_session:
            raise ValueError(f"Analysis session not found: {analysis_session_id}")
        
        collection_ids = json.loads(analysis_session.collection_ids)
        
        # Delete embeddings
        deleted_count = vector_storage.delete_embeddings(collection_ids=collection_ids)
        
        return {
            'status': 'completed',
            'message': f'Deleted {deleted_count} embeddings',
            'embeddings_deleted': deleted_count
        }


# Global content indexer instance
content_indexer = ContentIndexer()
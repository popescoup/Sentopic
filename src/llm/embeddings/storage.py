"""
Vector Embeddings Storage

Handles storage and retrieval of vector embeddings for semantic search.
Uses SQLite with vector extensions for efficient similarity search.

FIXED: Parameter binding issues with SQLAlchemy text() queries
"""

import sqlite3
import numpy as np
import pickle
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from sqlalchemy import text
from ...database import db


@dataclass
class SearchResult:
    """Result from vector similarity search."""
    content_id: str
    content_type: str  # 'post' or 'comment'
    collection_id: str
    similarity_score: float
    content_text: str = ""
    metadata: Dict[str, Any] = None


class VectorStorage:
    """
    Vector storage system for embeddings.
    
    Stores embeddings in SQLite database and provides similarity search.
    Uses cosine similarity for finding related content.
    """
    
    def __init__(self, db_path: str = "sentopic.db"):
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure vector storage tables exist."""
        # Use the existing database connection
        session = db.get_session()
        try:
            # Tables will be created by database.py updates
            # This is just to ensure they exist
            session.execute(text("SELECT 1 FROM content_embeddings LIMIT 1"))
        except Exception:
            # Tables don't exist yet - they'll be created by database schema updates
            pass
        finally:
            session.close()
    
    def store_embeddings(self, content_items: List[Dict[str, Any]], 
                        embeddings: np.ndarray, model: str, provider: str) -> int:
        """
        Store embeddings for content items.
        
        Args:
            content_items: List of content dictionaries with keys:
                          - content_id: unique identifier
                          - content_type: 'post' or 'comment'
                          - collection_id: collection identifier
                          - text: content text (optional, for storage)
            embeddings: Numpy array of embeddings (shape: [n_items, embedding_dim])
            model: Model name used to generate embeddings
            provider: Provider name used to generate embeddings
        
        Returns:
            Number of embeddings stored
        """
        if len(content_items) != len(embeddings):
            raise ValueError("Number of content items must match number of embeddings")
        
        session = db.get_session()
        try:
            stored_count = 0
            
            for i, (content_item, embedding) in enumerate(zip(content_items, embeddings)):
                # Serialize embedding as blob
                embedding_blob = pickle.dumps(embedding.astype(np.float32))
                
                # FIXED: Use dictionary parameters instead of positional
                session.execute(text("""
                    INSERT OR REPLACE INTO content_embeddings 
                    (content_type, content_id, collection_id, embedding, model, provider, created_at)
                    VALUES (:content_type, :content_id, :collection_id, :embedding, :model, :provider, :created_at)
                """), {
                    'content_type': content_item['content_type'],
                    'content_id': content_item['content_id'],
                    'collection_id': content_item['collection_id'],
                    'embedding': embedding_blob,
                    'model': model,
                    'provider': provider,
                    'created_at': int(np.datetime64('now').astype('datetime64[s]').astype(int))
                })
                
                stored_count += 1
            
            session.commit()
            return stored_count
            
        finally:
            session.close()
    
    def search_similar(self, query_embedding: np.ndarray, 
                      collection_ids: Optional[List[str]] = None,
                      content_types: Optional[List[str]] = None,
                      limit: int = 10, 
                      min_similarity: float = 0.0) -> List[SearchResult]:
        """
        Search for similar content using vector similarity.
        
        Args:
            query_embedding: Query embedding vector
            collection_ids: Filter by collection IDs (optional)
            content_types: Filter by content types (optional)
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of SearchResult objects sorted by similarity (descending)
        """
        session = db.get_session()
        try:
            # Build query conditions and parameters using dictionary format
            conditions = []
            params = {}
            
            if collection_ids:
                # FIXED: Use dictionary parameters with IN clause
                collection_placeholders = ','.join([f':collection_id_{i}' for i in range(len(collection_ids))])
                conditions.append(f"collection_id IN ({collection_placeholders})")
                for i, collection_id in enumerate(collection_ids):
                    params[f'collection_id_{i}'] = collection_id
            
            if content_types:
                # FIXED: Use dictionary parameters with IN clause
                type_placeholders = ','.join([f':content_type_{i}' for i in range(len(content_types))])
                conditions.append(f"content_type IN ({type_placeholders})")
                for i, content_type in enumerate(content_types):
                    params[f'content_type_{i}'] = content_type
            
            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
            
            # Fetch all embeddings (we'll compute similarity in Python)
            query_text = f"""
                SELECT content_id, content_type, collection_id, embedding 
                FROM content_embeddings 
                {where_clause}
            """
            
            # FIXED: Use dictionary parameters
            results = session.execute(text(query_text), params).fetchall()
            
            if not results:
                return []
            
            # Compute similarities
            similarities = []
            query_norm = np.linalg.norm(query_embedding)
            
            for row in results:
                content_id, content_type, collection_id, embedding_blob = row
                
                # Deserialize embedding
                try:
                    stored_embedding = pickle.loads(embedding_blob)
                    
                    # Compute cosine similarity
                    stored_norm = np.linalg.norm(stored_embedding)
                    if query_norm > 0 and stored_norm > 0:
                        similarity = np.dot(query_embedding, stored_embedding) / (query_norm * stored_norm)
                    else:
                        similarity = 0.0
                    
                    # Filter by minimum similarity
                    if similarity >= min_similarity:
                        similarities.append((
                            content_id, content_type, collection_id, float(similarity)
                        ))
                        
                except Exception:
                    # Skip corrupted embeddings
                    continue
            
            # Sort by similarity (descending) and limit
            similarities.sort(key=lambda x: x[3], reverse=True)
            similarities = similarities[:limit]
            
            # Create SearchResult objects with content text
            search_results = []
            for content_id, content_type, collection_id, similarity in similarities:
                # Fetch actual content text
                content_text = self._fetch_content_text(content_id, content_type, collection_id, session)
                
                search_results.append(SearchResult(
                    content_id=content_id,
                    content_type=content_type,
                    collection_id=collection_id,
                    similarity_score=similarity,
                    content_text=content_text
                ))
            
            return search_results
            
        finally:
            session.close()
    
    def _fetch_content_text(self, content_id: str, content_type: str, 
                           collection_id: str, session) -> str:
        """Fetch the actual text content for a given item."""
        try:
            if content_type == 'post':
                # FIXED: Use dictionary parameters
                result = session.execute(text("""
                    SELECT title, content 
                    FROM posts 
                    WHERE reddit_id = :content_id AND collection_id = :collection_id
                """), {
                    'content_id': content_id, 
                    'collection_id': collection_id
                }).fetchone()
                
                if result:
                    title, content = result
                    return f"{title} {content or ''}".strip()
            
            elif content_type == 'comment':
                # FIXED: Use dictionary parameters
                result = session.execute(text("""
                    SELECT content 
                    FROM comments 
                    WHERE reddit_id = :content_id AND collection_id = :collection_id
                """), {
                    'content_id': content_id,
                    'collection_id': collection_id
                }).fetchone()
                
                if result:
                    return result[0] or ""
            
        except Exception:
            pass
        
        return ""
    
    def get_embedding_stats(self, collection_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get statistics about stored embeddings.
        
        Args:
            collection_ids: Filter by collection IDs (optional)
        
        Returns:
            Dictionary with embedding statistics
        """
        session = db.get_session()
        try:
            # Build conditions and parameters using dictionary format
            conditions = []
            params = {}
            
            if collection_ids:
                # FIXED: Use dictionary parameters with IN clause
                collection_placeholders = ','.join([f':collection_id_{i}' for i in range(len(collection_ids))])
                conditions.append(f"collection_id IN ({collection_placeholders})")
                for i, collection_id in enumerate(collection_ids):
                    params[f'collection_id_{i}'] = collection_id
            
            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
            
            # Get total counts
            total_result = session.execute(text(f"""
                SELECT COUNT(*) FROM content_embeddings {where_clause}
            """), params).fetchone()
            
            total_embeddings = total_result[0] if total_result else 0
            
            # Get counts by content type
            type_results = session.execute(text(f"""
                SELECT content_type, COUNT(*) 
                FROM content_embeddings {where_clause}
                GROUP BY content_type
            """), params).fetchall()
            
            type_counts = {content_type: count for content_type, count in type_results}
            
            # Get model usage
            model_results = session.execute(text(f"""
                SELECT model, provider, COUNT(*) 
                FROM content_embeddings {where_clause}
                GROUP BY model, provider
            """), params).fetchall()
            
            model_usage = []
            for model, provider, count in model_results:
                model_usage.append({
                    'model': model,
                    'provider': provider,
                    'count': count
                })
            
            return {
                'total_embeddings': total_embeddings,
                'by_content_type': type_counts,
                'by_model': model_usage
            }
            
        finally:
            session.close()
    
    def delete_embeddings(self, collection_ids: Optional[List[str]] = None,
                         content_types: Optional[List[str]] = None) -> int:
        """
        Delete embeddings matching the given criteria.
        
        Args:
            collection_ids: Delete embeddings for these collections (optional)
            content_types: Delete embeddings for these content types (optional)
        
        Returns:
            Number of embeddings deleted
        """
        session = db.get_session()
        try:
            # Build conditions and parameters using dictionary format
            conditions = []
            params = {}
            
            if collection_ids:
                # FIXED: Use dictionary parameters with IN clause
                collection_placeholders = ','.join([f':collection_id_{i}' for i in range(len(collection_ids))])
                conditions.append(f"collection_id IN ({collection_placeholders})")
                for i, collection_id in enumerate(collection_ids):
                    params[f'collection_id_{i}'] = collection_id
            
            if content_types:
                # FIXED: Use dictionary parameters with IN clause
                type_placeholders = ','.join([f':content_type_{i}' for i in range(len(content_types))])
                conditions.append(f"content_type IN ({type_placeholders})")
                for i, content_type in enumerate(content_types):
                    params[f'content_type_{i}'] = content_type
            
            if not conditions:
                raise ValueError("Must specify at least one deletion criteria")
            
            where_clause = "WHERE " + " AND ".join(conditions)
            
            # Count before deletion
            count_result = session.execute(text(f"""
                SELECT COUNT(*) FROM content_embeddings {where_clause}
            """), params).fetchone()
            
            count_before = count_result[0] if count_result else 0
            
            # Delete embeddings
            session.execute(text(f"""
                DELETE FROM content_embeddings {where_clause}
            """), params)
            
            session.commit()
            return count_before
            
        finally:
            session.close()
    
    def embedding_exists(self, content_id: str, content_type: str, 
                        collection_id: str) -> bool:
        """
        Check if an embedding exists for the given content.
        
        Args:
            content_id: Content identifier
            content_type: 'post' or 'comment'
            collection_id: Collection identifier
        
        Returns:
            True if embedding exists
        """
        session = db.get_session()
        try:
            # FIXED: Use dictionary parameters
            result = session.execute(text("""
                SELECT 1 FROM content_embeddings 
                WHERE content_id = :content_id AND content_type = :content_type AND collection_id = :collection_id
            """), {
                'content_id': content_id,
                'content_type': content_type,
                'collection_id': collection_id
            }).fetchone()
            
            return result is not None
            
        finally:
            session.close()


# Global vector storage instance
vector_storage = VectorStorage()
"""
Discussion Builder Service

Builds complete Reddit discussion contexts by intelligently grouping related
posts and comments into coherent conversation threads for RAG consumption.
"""

from typing import Dict, List, Any, Optional, Tuple
from ...database import db, Post, Comment


class DiscussionBuilder:
    """
    Builds complete discussion contexts from individual Reddit posts and comments.
    
    When search finds a relevant piece of content, this service reconstructs
    the full conversational context around it for optimal LLM understanding.
    """
    
    def __init__(self):
        self.max_comments_per_post = 10  # Limit to most relevant comments
        self.max_comment_depth = 3       # Limit threading depth for readability
    
    def build_discussion_from_post(self, post_id: str, collection_id: str) -> Dict[str, Any]:
        """
        Build complete discussion context starting from a post.
        
        Args:
            post_id: Reddit ID of the post
            collection_id: Collection containing the post
        
        Returns:
            Dictionary with complete discussion context
        """
        session = db.get_session()
        try:
            # Get the main post
            post = session.query(Post).filter(
                Post.reddit_id == post_id,
                Post.collection_id == collection_id
            ).first()
            
            if not post:
                return {'post': None, 'comments': []}
            
            # Convert post to dictionary
            post_data = self._post_to_dict(post)
            
            # Get related comments for this post
            comments = session.query(Comment).filter(
                Comment.post_reddit_id == post_id,
                Comment.collection_id == collection_id
            ).order_by(Comment.score.desc(), Comment.depth, Comment.position).all()
            
            # Select and format best comments
            selected_comments = self._select_best_comments(comments)
            comments_data = [self._comment_to_dict(comment) for comment in selected_comments]
            
            return {
                'post': post_data,
                'comments': comments_data,
                'discussion_type': 'post_with_comments',
                'total_comments_available': len(comments),
                'comments_included': len(comments_data)
            }
            
        finally:
            session.close()
    
    def build_discussion_from_comment(self, comment_id: str, collection_id: str) -> Dict[str, Any]:
        """
        Build complete discussion context starting from a comment.
        
        Args:
            comment_id: Reddit ID of the comment
            collection_id: Collection containing the comment
        
        Returns:
            Dictionary with complete discussion context
        """
        session = db.get_session()
        try:
            # Get the target comment
            target_comment = session.query(Comment).filter(
                Comment.reddit_id == comment_id,
                Comment.collection_id == collection_id
            ).first()
            
            if not target_comment:
                return {'post': None, 'comments': []}
            
            # Get the parent post
            post = session.query(Post).filter(
                Post.reddit_id == target_comment.post_reddit_id,
                Post.collection_id == collection_id
            ).first()
            
            post_data = self._post_to_dict(post) if post else None
            
            # Get the comment thread around this comment
            thread_comments = self._build_comment_thread(target_comment, session)
            comments_data = [self._comment_to_dict(comment) for comment in thread_comments]
            
            return {
                'post': post_data,
                'comments': comments_data,
                'discussion_type': 'comment_focused',
                'target_comment_id': comment_id,
                'comments_included': len(comments_data)
            }
            
        finally:
            session.close()
    
    def build_multiple_discussions(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build discussion contexts for multiple search results.
        
        Args:
            search_results: List of search result dictionaries
        
        Returns:
            List of discussion contexts
        """
        discussions = []
        
        # Group results by post to avoid duplicating discussions
        processed_posts = set()
        
        for result in search_results:
            content_id = result['content_id']
            content_type = result['content_type']
            collection_id = result['collection_id']
            
            if content_type == 'post':
                if content_id not in processed_posts:
                    discussion = self.build_discussion_from_post(content_id, collection_id)
                    if discussion['post']:
                        discussions.append(discussion)
                        processed_posts.add(content_id)
            
            elif content_type == 'comment':
                # For comments, get the parent post ID to check for duplicates
                parent_post_id = self._get_parent_post_id(content_id, collection_id)
                if parent_post_id and parent_post_id not in processed_posts:
                    discussion = self.build_discussion_from_comment(content_id, collection_id)
                    if discussion['post']:
                        discussions.append(discussion)
                        processed_posts.add(parent_post_id)
        
        return discussions
    
    def get_representative_examples(self, collection_ids: List[str], 
                                  keywords: List[str], limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get representative discussion examples for a set of keywords and collections.
        
        Args:
            collection_ids: Collections to search in
            keywords: Keywords to find examples for
            limit: Maximum number of examples
        
        Returns:
            List of representative discussion contexts
        """
        session = db.get_session()
        try:
            examples = []
            
            # Find high-quality posts that contain keywords
            posts = session.query(Post).filter(
                Post.collection_id.in_(collection_ids),
                Post.score > 10  # Filter for posts with decent engagement
            ).order_by(Post.score.desc()).limit(limit * 3).all()  # Get more to filter from
            
            for post in posts:
                # Check if post contains any keywords
                content_to_search = (post.title + " " + (post.content or "")).lower()
                if any(keyword.lower() in content_to_search for keyword in keywords):
                    discussion = self.build_discussion_from_post(post.reddit_id, post.collection_id)
                    if discussion['post']:
                        examples.append(discussion)
                        if len(examples) >= limit:
                            break
            
            return examples
            
        finally:
            session.close()
    
    def _select_best_comments(self, comments: List[Comment]) -> List[Comment]:
        """
        Select the most relevant comments for inclusion in discussion context.
        
        Args:
            comments: All available comments for a post
        
        Returns:
            Filtered list of best comments
        """
        if not comments:
            return []
        
        selected = []
        
        # Always include root comments (direct replies to post) first
        root_comments = [c for c in comments if c.is_root and c.depth == 0]
        root_comments.sort(key=lambda c: c.score, reverse=True)
        
        # Take top root comments
        selected.extend(root_comments[:5])
        
        # Add some high-quality replies if space allows
        reply_comments = [c for c in comments if not c.is_root and c.depth <= self.max_comment_depth]
        reply_comments.sort(key=lambda c: c.score, reverse=True)
        
        remaining_slots = self.max_comments_per_post - len(selected)
        selected.extend(reply_comments[:remaining_slots])
        
        # Sort by depth and position to maintain thread structure
        selected.sort(key=lambda c: (c.depth, c.position))
        
        return selected
    
    def _build_comment_thread(self, target_comment: Comment, session) -> List[Comment]:
        """
        Build a focused comment thread around a target comment.
        
        Args:
            target_comment: The comment to build context around
            session: Database session
        
        Returns:
            List of comments that form the thread context
        """
        thread_comments = []
        
        # Always include the target comment
        thread_comments.append(target_comment)
        
        # If it's a root comment, get some replies
        if target_comment.is_root:
            replies = session.query(Comment).filter(
                Comment.post_reddit_id == target_comment.post_reddit_id,
                Comment.collection_id == target_comment.collection_id,
                Comment.parent_reddit_id == target_comment.reddit_id
            ).order_by(Comment.score.desc()).limit(3).all()
            thread_comments.extend(replies)
        
        else:
            # If it's a reply, get the parent comment and some sibling replies
            if target_comment.parent_reddit_id:
                parent = session.query(Comment).filter(
                    Comment.reddit_id == target_comment.parent_reddit_id,
                    Comment.collection_id == target_comment.collection_id
                ).first()
                
                if parent:
                    thread_comments.append(parent)
                    
                    # Get other replies to the same parent
                    siblings = session.query(Comment).filter(
                        Comment.parent_reddit_id == target_comment.parent_reddit_id,
                        Comment.collection_id == target_comment.collection_id,
                        Comment.reddit_id != target_comment.reddit_id
                    ).order_by(Comment.score.desc()).limit(2).all()
                    thread_comments.extend(siblings)
        
        # Sort by depth and position to maintain structure
        thread_comments.sort(key=lambda c: (c.depth, c.position))
        
        return thread_comments
    
    def _get_parent_post_id(self, comment_id: str, collection_id: str) -> Optional[str]:
        """Get the parent post ID for a comment."""
        session = db.get_session()
        try:
            comment = session.query(Comment).filter(
                Comment.reddit_id == comment_id,
                Comment.collection_id == collection_id
            ).first()
            return comment.post_reddit_id if comment else None
        finally:
            session.close()
    
    def _post_to_dict(self, post: Post) -> Dict[str, Any]:
        """Convert Post object to dictionary."""
        if not post:
            return {}
        
        return {
            'reddit_id': post.reddit_id,
            'collection_id': post.collection_id,
            'subreddit': post.subreddit,
            'title': post.title,
            'content': post.content or '',
            'author': post.author,
            'score': post.score,
            'upvote_ratio': post.upvote_ratio,
            'created_utc': post.created_utc,
            'url': post.url,
            'is_self': post.is_self
        }
    
    def _comment_to_dict(self, comment: Comment) -> Dict[str, Any]:
        """Convert Comment object to dictionary."""
        if not comment:
            return {}
        
        return {
            'reddit_id': comment.reddit_id,
            'collection_id': comment.collection_id,
            'post_reddit_id': comment.post_reddit_id,
            'parent_reddit_id': comment.parent_reddit_id,
            'content': comment.content,
            'author': comment.author,
            'score': comment.score,
            'created_utc': comment.created_utc,
            'is_root': comment.is_root,
            'depth': comment.depth,
            'position': comment.position
        }


# Global discussion builder instance
discussion_builder = DiscussionBuilder()
import praw
import time
from typing import Optional, List, Dict, Any
from .config import config
from typing import Tuple
import requests


class RedditClient:
    def __init__(self):
        self.reddit = None
        self._initialize_client()
        self.rate_limit_delay = 0.5  # Seconds between requests

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test Reddit API connection.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not self.reddit:
                return False, "Reddit client not initialized"
            
            # Test connection by trying to access a subreddit
            # This uses the existing PRAW client which is already configured
            test_subreddit = self.reddit.subreddit('test')
            
            # Try to get one post to test the connection
            posts = list(test_subreddit.hot(limit=1))
            
            return True, "Connected successfully to Reddit API"
            
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    def _initialize_client(self):
        """Initialize the PRAW Reddit client."""
        
        # Force reload config to get latest values
        config.reload_config()

        reddit_config = config.get_reddit_config()
        
        self.reddit = praw.Reddit(
            client_id=reddit_config['client_id'],
            client_secret=reddit_config['client_secret'],
            user_agent=reddit_config['user_agent']
        )
        
        # Test the connection
        try:
            # This will raise an exception if credentials are invalid
            self.reddit.user.me()
        except Exception:
            # For read-only access, we don't need user authentication
            # Just test that we can access Reddit
            try:
                list(self.reddit.subreddit('test').hot(limit=1))
            except Exception as e:
                raise Exception(f"Failed to connect to Reddit API: {e}")
    
    def reload_client(self):
        """Force reload of client with new configuration."""
        self._initialize_client()
    
    def _rate_limit_sleep(self):
        """Sleep to respect Reddit's rate limits."""
        time.sleep(self.rate_limit_delay)
    
    def get_posts(self, subreddit: str, sort_method: str, time_period: Optional[str] = None, 
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get posts from a subreddit.
        
        Args:
            subreddit: Subreddit name (without r/)
            sort_method: 'hot', 'new', 'rising', 'top', or 'controversial'
            time_period: For top/controversial: 'hour', 'day', 'week', 'month', 'year', 'all'
            limit: Number of posts to retrieve
        
        Returns:
            List of post dictionaries
        """
        posts = []
        
        try:
            sub = self.reddit.subreddit(subreddit)
            
            # Get submissions based on sort method (single API call for all posts)
            if sort_method == 'hot':
                submissions = sub.hot(limit=limit)
            elif sort_method == 'new':
                submissions = sub.new(limit=limit)
            elif sort_method == 'rising':
                submissions = sub.rising(limit=limit)
            elif sort_method == 'top':
                submissions = sub.top(time_filter=time_period or 'day', limit=limit)
            elif sort_method == 'controversial':
                submissions = sub.controversial(time_filter=time_period or 'day', limit=limit)
            else:
                raise ValueError(f"Invalid sort method: {sort_method}")
            
            # Process all fetched posts (no additional API calls needed)
            for submission in submissions:
                post_data = {
                    'id': submission.id,
                    'subreddit': submission.subreddit.display_name,
                    'title': submission.title,
                    'content': getattr(submission, 'selftext', '') or '',  # Text posts only
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'score': submission.score,
                    'upvote_ratio': submission.upvote_ratio,  # Reddit's upvote ratio metric
                    'created_utc': int(submission.created_utc),
                    'url': submission.url,
                    'is_self': submission.is_self  # True for text posts, False for links
                }
                posts.append(post_data)
            
            # Rate limit after fetching all posts
            self._rate_limit_sleep()
        
        except Exception as e:
            print(f"Error fetching posts from r/{subreddit}: {e}")
            raise
        
        return posts
    
    def get_comments(self, post_id: str, root_comments_limit: int, 
                    replies_per_root: int, min_upvotes: int) -> List[Dict[str, Any]]:
        """
        Get comments for a specific post with hierarchical tracking.
        
        Args:
            post_id: Reddit post ID
            root_comments_limit: Maximum number of root comments to collect
            replies_per_root: Maximum number of replies per root comment
            min_upvotes: Minimum upvotes required for comments
        
        Returns:
            List of comment dictionaries with depth and position tracking
        """
        comments = []
        
        try:
            # Single API call to get the entire comment tree for this post
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # Remove "load more comments"
            
            # Rate limit only after the API call, not during processing
            self._rate_limit_sleep()
            
            root_comments_collected = 0
            
            # Process root comments (depth=0)
            for root_position, comment in enumerate(submission.comments, 1):
                # Check if this root comment meets criteria
                if (comment.score >= min_upvotes and 
                    root_comments_collected < root_comments_limit):
                    
                    # Add root comment
                    comment_data = {
                        'id': comment.id,
                        'post_id': post_id,
                        'parent_id': None,  # Root comment
                        'content': comment.body,
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'score': comment.score,
                        'created_utc': int(comment.created_utc),
                        'is_root': True,
                        'depth': 0,
                        'position': root_position
                    }
                    comments.append(comment_data)
                    root_comments_collected += 1
                    
                    # Process replies to this root comment with depth tracking
                    self._process_replies(
                        comment.replies, 
                        post_id, 
                        comment.id, 
                        depth=1, 
                        max_replies=replies_per_root, 
                        min_upvotes=min_upvotes,
                        comments=comments
                    )
        
        except Exception as e:
            print(f"Error fetching comments for post {post_id}: {e}")
            # Don't raise here - we want to continue with other posts
        
        return comments
    
    def _process_replies(self, replies, post_id: str, parent_id: str, depth: int, 
                        max_replies: int, min_upvotes: int, comments: List[Dict[str, Any]]):
        """
        Recursively process comment replies with depth and position tracking.
        
        Args:
            replies: PRAW CommentForest or list of replies
            post_id: Reddit post ID
            parent_id: Parent comment ID
            depth: Current nesting depth
            max_replies: Maximum number of replies to collect at this level
            min_upvotes: Minimum upvotes required
            comments: List to append processed comments to
        """
        replies_collected = 0
        
        for reply_position, reply in enumerate(replies, 1):
            if (reply.score >= min_upvotes and 
                replies_collected < max_replies):
                
                reply_data = {
                    'id': reply.id,
                    'post_id': post_id,
                    'parent_id': parent_id,
                    'content': reply.body,
                    'author': str(reply.author) if reply.author else '[deleted]',
                    'score': reply.score,
                    'created_utc': int(reply.created_utc),
                    'is_root': False,
                    'depth': depth,
                    'position': reply_position
                }
                comments.append(reply_data)
                replies_collected += 1
                
                # Recursively process replies to this reply (limited depth to avoid infinite recursion)
                if depth < 5 and hasattr(reply, 'replies') and len(reply.replies) > 0:
                    self._process_replies(
                        reply.replies,
                        post_id,
                        reply.id,
                        depth + 1,
                        max_replies,  # Same limit applies to all levels
                        min_upvotes,
                        comments
                    )


# Global Reddit client instance
reddit_client = RedditClient()
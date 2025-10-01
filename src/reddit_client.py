import praw
import time
from typing import Optional, List, Dict, Any
from .config import config
from typing import Tuple
import requests


class RedditClient:
    def __init__(self):
        self.reddit = None
        self.rate_limit_delay = 0.5  # Seconds between requests
        # Don't initialize immediately - will be done on first use or explicit call

    def _ensure_initialized(self):
        """Ensure the Reddit client is initialized before use."""
        if self.reddit is None:
            self._initialize_client()

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test Reddit API connection.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Ensure client is initialized
            self._ensure_initialized()
            
            if not self.reddit:
                return False, "Reddit client not initialized"
            
            # Test connection by trying to access a subreddit
            # This uses the existing PRAW client which is already configured
            test_subreddit = self.reddit.subreddit('test')
            
            # Try to get one post to test the connection
            posts = list(test_subreddit.hot(limit=1))
            
            return True, "Connected successfully to Reddit API"
            
        except Exception as e:
            return False, f"Reddit connection test failed: {str(e)}"
    
    def _initialize_client(self):
        """Initialize the PRAW Reddit client."""
        
        print("=" * 60)
        print("DEBUG: RedditClient._initialize_client() called")
        print("=" * 60)
        
        # Force reload config to get latest values
        config.reload_config()

        reddit_config = config.get_reddit_config()
        
        print("DEBUG: Config values retrieved:")
        print(f"  client_id: '{reddit_config['client_id']}'")
        print(f"  client_id type: {type(reddit_config['client_id'])}")
        print(f"  client_secret: '{reddit_config['client_secret'][:5]}...'")
        print(f"  client_secret type: {type(reddit_config['client_secret'])}")
        print(f"  user_agent: '{reddit_config['user_agent']}'")
        print(f"  user_agent type: {type(reddit_config['user_agent'])}")
        print("=" * 60)
        
        print("DEBUG: Creating PRAW Reddit instance with all explicit config...")
        try:
            # Pass all config directly to avoid PRAW's config discovery
            self.reddit = praw.Reddit(
                client_id=reddit_config['client_id'],
                client_secret=reddit_config['client_secret'],
                user_agent=reddit_config['user_agent'],
                redirect_uri='http://localhost:8080',
                comment_kind='t1',
                message_kind='t4',
                redditor_kind='t2',
                submission_kind='t3',
                subreddit_kind='t5',
                trophy_kind='t6',
                oauth_url='https://oauth.reddit.com',
                reddit_url='https://www.reddit.com',
                short_url='https://redd.it',
                ratelimit_seconds=5,
                timeout=16,
                check_for_async=False,
                check_for_updates=False
            )
            print(f"DEBUG: PRAW Reddit instance created successfully")
            print("=" * 60)
        except Exception as e:
            print(f"ERROR: Failed to create PRAW Reddit instance!")
            print(f"  Exception type: {type(e).__name__}")
            print(f"  Exception message: {str(e)}")
            import traceback
            print(f"  Full traceback:\n{traceback.format_exc()}")
            print("=" * 60)
            raise
        
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
        self.reddit = None  # Reset to force reinitialization
        self._initialize_client()
    
    def _rate_limit_sleep(self):
        """Sleep to respect Reddit's rate limits."""
        time.sleep(self.rate_limit_delay)
    
    def get_posts(self, subreddit: str, sort_method: str, time_period: Optional[str] = None, 
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get posts from a subreddit.
        ...
        """
        # Ensure client is initialized before use
        self._ensure_initialized()
        
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
        ...
        """
        # Ensure client is initialized before use
        self._ensure_initialized()
        
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


# Global Reddit client instance (lazy initialization)
_reddit_client_instance = None

def get_reddit_client() -> RedditClient:
    """
    Get the global Reddit client instance, creating it if necessary.
    This implements lazy initialization to avoid timing issues in PyInstaller.
    """
    global _reddit_client_instance
    if _reddit_client_instance is None:
        _reddit_client_instance = RedditClient()
    return _reddit_client_instance

def is_reddit_client_initialized() -> bool:
    """Check if the Reddit client has been initialized."""
    return _reddit_client_instance is not None

def reset_reddit_client():
    """Reset the Reddit client instance (useful for configuration changes)."""
    global _reddit_client_instance
    _reddit_client_instance = None
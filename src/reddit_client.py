import praw
import time
from typing import Optional, List, Dict, Any
from .config import config


class RedditClient:
    def __init__(self):
        self.reddit = None
        self._initialize_client()
        self.rate_limit_delay = 1  # Seconds between requests
    
    def _initialize_client(self):
        """Initialize the PRAW Reddit client."""
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
            
            # Get submissions based on sort method
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
            
            for submission in submissions:
                self._rate_limit_sleep()
                
                post_data = {
                    'id': submission.id,
                    'subreddit': submission.subreddit.display_name,
                    'title': submission.title,
                    'content': getattr(submission, 'selftext', '') or '',  # Text posts only
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'score': submission.score,
                    'created_utc': int(submission.created_utc),
                    'url': submission.url
                }
                posts.append(post_data)
        
        except Exception as e:
            print(f"Error fetching posts from r/{subreddit}: {e}")
            raise
        
        return posts
    
    def get_comments(self, post_id: str, root_comments_limit: int, 
                    replies_per_root: int, min_upvotes: int) -> List[Dict[str, Any]]:
        """
        Get comments for a specific post.
        
        Args:
            post_id: Reddit post ID
            root_comments_limit: Maximum number of root comments to collect
            replies_per_root: Maximum number of replies per root comment
            min_upvotes: Minimum upvotes required for comments
        
        Returns:
            List of comment dictionaries
        """
        comments = []
        
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # Remove "load more comments"
            
            root_comments_collected = 0
            
            for comment in submission.comments:
                self._rate_limit_sleep()
                
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
                        'is_root': True
                    }
                    comments.append(comment_data)
                    root_comments_collected += 1
                    
                    # Get replies to this root comment
                    replies_collected = 0
                    for reply in comment.replies:
                        self._rate_limit_sleep()
                        
                        if (reply.score >= min_upvotes and 
                            replies_collected < replies_per_root):
                            
                            reply_data = {
                                'id': reply.id,
                                'post_id': post_id,
                                'parent_id': comment.id,  # Points to root comment
                                'content': reply.body,
                                'author': str(reply.author) if reply.author else '[deleted]',
                                'score': reply.score,
                                'created_utc': int(reply.created_utc),
                                'is_root': False
                            }
                            comments.append(reply_data)
                            replies_collected += 1
        
        except Exception as e:
            print(f"Error fetching comments for post {post_id}: {e}")
            # Don't raise here - we want to continue with other posts
        
        return comments


# Global Reddit client instance
reddit_client = RedditClient()
from typing import Optional
from tqdm import tqdm
from .database import db
from .reddit_client import reddit_client


class CollectionParameters:
    def __init__(self, subreddit: str, sort_method: str, time_period: Optional[str],
                 posts_count: int, root_comments: int, replies_per_root: int, 
                 min_upvotes: int):
        self.subreddit = subreddit
        self.sort_method = sort_method
        self.time_period = time_period
        self.posts_count = posts_count
        self.root_comments = root_comments
        self.replies_per_root = replies_per_root
        self.min_upvotes = min_upvotes
        
        # Validate parameters
        self._validate()
    
    def _validate(self):
        """Validate collection parameters."""
        valid_sort_methods = ['hot', 'new', 'rising', 'top', 'controversial']
        if self.sort_method not in valid_sort_methods:
            raise ValueError(f"Sort method must be one of: {valid_sort_methods}")
        
        if self.sort_method in ['top', 'controversial'] and not self.time_period:
            raise ValueError(f"Time period is required for sort method '{self.sort_method}'")
        
        valid_time_periods = ['hour', 'day', 'week', 'month', 'year', 'all']
        if self.time_period and self.time_period not in valid_time_periods:
            raise ValueError(f"Time period must be one of: {valid_time_periods}")
        
        if self.posts_count <= 0:
            raise ValueError("Posts count must be greater than 0")
        
        if self.root_comments < 0:
            raise ValueError("Root comments must be 0 or greater")
        
        if self.replies_per_root < 0:
            raise ValueError("Replies per root must be 0 or greater")


class RedditCollector:
    def __init__(self):
        self.current_collection_id = None
    
    def collect_data(self, params: CollectionParameters) -> str:
        """
        Collect Reddit data based on the provided parameters.
        
        Args:
            params: Collection parameters object
        
        Returns:
            Collection ID for the completed collection
        """
        # Create collection record
        collection_id = db.create_collection(
            subreddit=params.subreddit,
            sort_method=params.sort_method,
            time_period=params.time_period,
            posts_requested=params.posts_count,
            root_comments_requested=params.root_comments,
            replies_per_root=params.replies_per_root,
            min_upvotes=params.min_upvotes
        )
        
        self.current_collection_id = collection_id
        
        try:
            print(f"Starting collection from r/{params.subreddit}")
            print(f"Sort: {params.sort_method}" + 
                  (f" ({params.time_period})" if params.time_period else ""))
            print(f"Collecting {params.posts_count} posts with up to "
                  f"{params.root_comments} root comments each "
                  f"(up to {params.replies_per_root} replies per root comment)")
            print(f"Minimum upvotes: {params.min_upvotes}")
            print()
            
            # Collect posts
            posts = self._collect_posts(params)
            
            if not posts:
                print("No posts collected. Collection failed.")
                db.update_collection_status(collection_id, 'failed')
                return collection_id
            
            # Collect comments for each post
            self._collect_comments_for_posts(posts, params)
            
            # Mark collection as completed
            db.update_collection_status(collection_id, 'completed')
            print(f"\nCollection completed successfully! Collection ID: {collection_id}")
            
        except Exception as e:
            print(f"\nCollection failed: {e}")
            db.update_collection_status(collection_id, 'failed')
            raise
        
        return collection_id
    
    def _collect_posts(self, params: CollectionParameters) -> list:
        """Collect posts with progress bar."""
        print("Fetching posts...")
        
        posts = reddit_client.get_posts(
            subreddit=params.subreddit,
            sort_method=params.sort_method,
            time_period=params.time_period,
            limit=params.posts_count
        )
        
        if not posts:
            return []
        
        # Save posts to database with progress bar
        with tqdm(total=len(posts), desc="Saving posts", unit="post") as pbar:
            for post in posts:
                db.save_post(post, self.current_collection_id)
                pbar.update(1)
        
        print(f"Collected {len(posts)} posts")
        return posts
    
    def _collect_comments_for_posts(self, posts: list, params: CollectionParameters):
        """Collect comments for all posts with progress bar."""
        if params.root_comments == 0:
            print("Skipping comment collection (root_comments = 0)")
            return
        
        print("\nFetching comments...")
        total_comments_collected = 0
        
        with tqdm(total=len(posts), desc="Processing posts", unit="post") as pbar:
            for post in posts:
                # Get comments for this post
                comments = reddit_client.get_comments(
                    post_id=post['id'],
                    root_comments_limit=params.root_comments,
                    replies_per_root=params.replies_per_root,
                    min_upvotes=params.min_upvotes
                )
                
                # Save comments to database
                for comment in comments:
                    db.save_comment(comment, self.current_collection_id)
                    total_comments_collected += 1
                
                pbar.update(1)
        
        print(f"Collected {total_comments_collected} comments total")


# Global collector instance
collector = RedditCollector()
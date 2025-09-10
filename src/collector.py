from typing import Optional, List, Dict, Any
from tqdm import tqdm
from .database import db, Post, Comment
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
        # Force reddit client to reload config before collection
        reddit_client.reload_client()

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
        
        # Save posts to database using bulk method
        self._save_posts(posts, self.current_collection_id)
        return posts
    
    def _collect_comments_for_posts(self, posts: list, params: CollectionParameters):
        """Collect comments for all posts with progress bar."""
        if params.root_comments == 0:
            print("Skipping comment collection (root_comments = 0)")
            return
        
        print("\nFetching comments...")
        all_comments = []
        
        with tqdm(total=len(posts), desc="Processing posts", unit="post") as pbar:
            for post in posts:
                # Get comments for this post
                comments = reddit_client.get_comments(
                    post_id=post['id'],
                    root_comments_limit=params.root_comments,
                    replies_per_root=params.replies_per_root,
                    min_upvotes=params.min_upvotes
                )
                
                all_comments.extend(comments)
                pbar.update(1)
        
        # Save all comments using bulk method
        self._save_comments(all_comments, self.current_collection_id)
    
    def _save_posts(self, posts: List[Dict[str, Any]], collection_id: str):
        """Save posts to database."""
        print(f"Saving {len(posts)} posts...")
        
        session = db.get_session()
        try:
            for post_data in tqdm(posts, desc="Saving posts", unit="post"):
                post = Post(
                    collection_id=collection_id,
                    reddit_id=post_data['id'],
                    subreddit=post_data['subreddit'],
                    title=post_data['title'],
                    content=post_data['content'],
                    author=post_data['author'],
                    score=post_data['score'],
                    upvote_ratio=post_data['upvote_ratio'],
                    created_utc=post_data['created_utc'],
                    url=post_data['url'],
                    is_self=post_data['is_self']
                )
                session.add(post)
            
            session.commit()
            print(f"Collected {len(posts)} posts")
        finally:
            session.close()

    def _save_comments(self, comments: List[Dict[str, Any]], collection_id: str):
        """Save comments to database."""
        if not comments:
            print("No comments to save")
            return
            
        print(f"Saving {len(comments)} comments...")
        
        session = db.get_session()
        try:
            for comment_data in tqdm(comments, desc="Saving comments", unit="comment"):
                comment = Comment(
                    collection_id=collection_id,
                    reddit_id=comment_data['id'],
                    post_reddit_id=comment_data['post_id'],
                    parent_reddit_id=comment_data['parent_id'],
                    content=comment_data['content'],
                    author=comment_data['author'],
                    score=comment_data['score'],
                    created_utc=comment_data['created_utc'],
                    is_root=comment_data['is_root'],
                    depth=comment_data['depth'],
                    position=comment_data['position']
                )
                session.add(comment)
            
            session.commit()
            print(f"Collected {len(comments)} comments")
        finally:
            session.close()


# Global collector instance
collector = RedditCollector()
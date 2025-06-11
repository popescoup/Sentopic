import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from typing import Optional, List

Base = declarative_base()


class Collection(Base):
    __tablename__ = 'collections'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subreddit = Column(String, nullable=False)
    sort_method = Column(String, nullable=False)
    time_period = Column(String, nullable=True)  # Only for top/controversial
    posts_requested = Column(Integer, nullable=False)
    root_comments_requested = Column(Integer, nullable=False)
    replies_per_root = Column(Integer, nullable=False)
    min_upvotes = Column(Integer, nullable=False)
    created_at = Column(Integer, nullable=False)
    status = Column(String, default='running')  # 'running', 'completed', 'failed'
    
    # Relationships (simplified - no cross-references between Post and Comment)
    posts = relationship("Post", back_populates="collection", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="collection", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = 'posts'
    
    # Composite primary key: collection_id + reddit_id
    collection_id = Column(String, ForeignKey('collections.id'), primary_key=True)
    reddit_id = Column(String, primary_key=True)  # Original Reddit post ID
    subreddit = Column(String, nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text)  # Self-text content for text posts
    author = Column(String)
    score = Column(Integer, default=0)
    upvote_ratio = Column(Float)  # Ratio of upvotes to total votes
    created_utc = Column(Integer)
    url = Column(String)
    is_self = Column(Boolean, default=False)  # True for text posts, False for link posts
    
    # Relationship to collection only
    collection = relationship("Collection", back_populates="posts")


class Comment(Base):
    __tablename__ = 'comments'
    
    # Composite primary key: collection_id + reddit_id
    collection_id = Column(String, ForeignKey('collections.id'), primary_key=True)
    reddit_id = Column(String, primary_key=True)  # Original Reddit comment ID
    post_reddit_id = Column(String, nullable=False)  # Which post this belongs to (references Post.reddit_id)
    parent_reddit_id = Column(String)  # For threading (None if root comment)
    content = Column(Text, nullable=False)  # Comment text content
    author = Column(String)
    score = Column(Integer, default=0)
    created_utc = Column(Integer)
    is_root = Column(Boolean, default=True)  # True for top-level comments
    depth = Column(Integer, default=0)  # Comment nesting depth (0=root, 1=reply, 2=reply to reply, etc.)
    position = Column(Integer, default=1)  # Position within the same depth level
    
    # Relationship to collection only
    collection = relationship("Collection", back_populates="comments")


class Database:
    def __init__(self, db_path: str = "sentopic.db"):
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def create_collection(self, subreddit: str, sort_method: str, time_period: Optional[str],
                         posts_requested: int, root_comments_requested: int, 
                         replies_per_root: int, min_upvotes: int) -> str:
        """Create a new collection record and return its ID."""
        session = self.get_session()
        try:
            collection = Collection(
                subreddit=subreddit,
                sort_method=sort_method,
                time_period=time_period,
                posts_requested=posts_requested,
                root_comments_requested=root_comments_requested,
                replies_per_root=replies_per_root,
                min_upvotes=min_upvotes,
                created_at=int(datetime.utcnow().timestamp())
            )
            session.add(collection)
            session.commit()
            return collection.id
        finally:
            session.close()
    
    def update_collection_status(self, collection_id: str, status: str):
        """Update the status of a collection."""
        session = self.get_session()
        try:
            collection = session.query(Collection).filter(Collection.id == collection_id).first()
            if collection:
                collection.status = status
                session.commit()
        finally:
            session.close()
    
    def save_post(self, post_data: dict, collection_id: str):
        """Save a Reddit post to the database."""
        session = self.get_session()
        try:
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
            session.add(post)  # Use add() instead of merge()
            session.commit()
        finally:
            session.close()
    
    def save_comment(self, comment_data: dict, collection_id: str):
        """Save a Reddit comment to the database."""
        session = self.get_session()
        try:
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
            session.add(comment)  # Use add() instead of merge()
            session.commit()
        finally:
            session.close()
    
    def get_collections(self) -> List[Collection]:
        """Get all collections."""
        session = self.get_session()
        try:
            return session.query(Collection).order_by(Collection.created_at.desc()).all()
        finally:
            session.close()


# Global database instance
db = Database()
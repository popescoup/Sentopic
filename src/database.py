import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey, Text
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
    
    # Relationships
    posts = relationship("Post", back_populates="collection", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="collection", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(String, primary_key=True)  # Reddit post ID
    subreddit = Column(String, nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=True)  # selftext for text posts
    author = Column(String, nullable=True)  # Can be None for deleted users
    score = Column(Integer, nullable=False)
    created_utc = Column(Integer, nullable=False)
    url = Column(Text, nullable=True)
    collection_id = Column(String, ForeignKey('collections.id'), nullable=False)
    
    # Relationships
    collection = relationship("Collection", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(String, primary_key=True)  # Reddit comment ID
    post_id = Column(String, ForeignKey('posts.id'), nullable=False)
    parent_id = Column(String, nullable=True)  # None for root comments, comment_id for replies
    content = Column(Text, nullable=False)
    author = Column(String, nullable=True)  # Can be None for deleted users
    score = Column(Integer, nullable=False)
    created_utc = Column(Integer, nullable=False)
    is_root = Column(Boolean, nullable=False)
    collection_id = Column(String, ForeignKey('collections.id'), nullable=False)
    
    # Relationships
    post = relationship("Post", back_populates="comments")
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
                id=post_data['id'],
                subreddit=post_data['subreddit'],
                title=post_data['title'],
                content=post_data['content'],
                author=post_data['author'],
                score=post_data['score'],
                created_utc=post_data['created_utc'],
                url=post_data['url'],
                collection_id=collection_id
            )
            session.merge(post)  # Use merge to handle duplicates
            session.commit()
        finally:
            session.close()
    
    def save_comment(self, comment_data: dict, collection_id: str):
        """Save a Reddit comment to the database."""
        session = self.get_session()
        try:
            comment = Comment(
                id=comment_data['id'],
                post_id=comment_data['post_id'],
                parent_id=comment_data['parent_id'],
                content=comment_data['content'],
                author=comment_data['author'],
                score=comment_data['score'],
                created_utc=comment_data['created_utc'],
                is_root=comment_data['is_root'],
                collection_id=collection_id
            )
            session.merge(comment)  # Use merge to handle duplicates
            session.commit()
        finally:
            session.close()
    
    def get_collections(self) -> List[Collection]:
        """Get all collections."""
        session = self.get_session()
        try:
            return session.query(Collection).all()
        finally:
            session.close()


# Global database instance
db = Database()
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey, Text, Float, Index, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from typing import Optional, List
import json

Base = declarative_base()


# Phase 1: Collection Tables (existing)

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

# Phase 2: Analytics Tables (existing)

class AnalysisSession(Base):
    __tablename__ = 'analysis_sessions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    keywords = Column(Text, nullable=False)  # JSON array of keywords
    collection_ids = Column(Text, nullable=False)  # JSON array of collection IDs
    created_at = Column(Integer, nullable=False)
    status = Column(String, default='created')  # 'running', 'completed', 'failed'
    total_mentions = Column(Integer, default=0)
    avg_sentiment = Column(Float, default=0.0)
    partial_matching = Column(Boolean, default=False)
    context_window_words = Column(Integer, default=20)
    
    # Relationships
    keyword_mentions = relationship("KeywordMention", back_populates="session", cascade="all, delete-orphan")
    keyword_stats = relationship("KeywordStat", back_populates="session", cascade="all, delete-orphan")
    keyword_cooccurrences = relationship("KeywordCooccurrence", back_populates="session", cascade="all, delete-orphan")
    llm_summary = relationship("LLMSummary", back_populates="session", uselist=False, cascade="all, delete-orphan")


class KeywordMention(Base):
    __tablename__ = 'keyword_mentions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_session_id = Column(String, ForeignKey('analysis_sessions.id'), nullable=False)
    keyword = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  # 'post' or 'comment'
    content_reddit_id = Column(String, nullable=False)  # references posts.reddit_id or comments.reddit_id
    collection_id = Column(String, nullable=False)
    sentiment_score = Column(Float, nullable=False)  # VADER sentiment score: -1 to +1
    created_utc = Column(Integer, nullable=False)  # copied from original post/comment
    position_in_content = Column(Integer, nullable=False)  # character index of keyword
    
    # Relationship
    session = relationship("AnalysisSession", back_populates="keyword_mentions")


class KeywordStat(Base):
    __tablename__ = 'keyword_stats'
    
    analysis_session_id = Column(String, ForeignKey('analysis_sessions.id'), primary_key=True)
    keyword = Column(String, primary_key=True)
    total_mentions = Column(Integer, nullable=False)
    avg_sentiment = Column(Float, nullable=False)
    posts_found_in = Column(Integer, nullable=False)
    comments_found_in = Column(Integer, nullable=False)
    collections_found_in = Column(Text, nullable=False)  # JSON array of collection IDs
    first_mention_date = Column(Integer, nullable=False)
    last_mention_date = Column(Integer, nullable=False)
    
    # Relationship
    session = relationship("AnalysisSession", back_populates="keyword_stats")


class KeywordCooccurrence(Base):
    __tablename__ = 'keyword_cooccurrences'
    
    analysis_session_id = Column(String, ForeignKey('analysis_sessions.id'), primary_key=True)
    keyword1 = Column(String, primary_key=True)  # alphabetically first keyword
    keyword2 = Column(String, primary_key=True)  # alphabetically second keyword
    cooccurrence_count = Column(Integer, nullable=False)
    in_posts = Column(Integer, nullable=False)
    in_comments = Column(Integer, nullable=False)
    avg_sentiment = Column(Float, nullable=True)
    
    # Relationship
    session = relationship("AnalysisSession", back_populates="keyword_cooccurrences")


# Phase 3: LLM Tables (new)

class LLMSummary(Base):
    __tablename__ = 'llm_summaries'
    
    analysis_session_id = Column(String, ForeignKey('analysis_sessions.id'), primary_key=True)
    user_query = Column(Text)  # Original user problem description
    summary_text = Column(Text, nullable=False)  # AI-generated summary
    generated_at = Column(Integer, nullable=False)
    provider_used = Column(String, nullable=False)  # 'anthropic', 'openai', etc.
    model_used = Column(String, nullable=False)  # Specific model name
    tokens_used = Column(Integer, default=0)
    cost_estimate = Column(Float, default=0.0)
    
    # Relationship
    session = relationship("AnalysisSession", back_populates="llm_summary")


class ContentEmbedding(Base):
    __tablename__ = 'content_embeddings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_type = Column(String, nullable=False)  # 'post' or 'comment'
    content_id = Column(String, nullable=False)  # reddit_id from posts or comments
    collection_id = Column(String, nullable=False)
    embedding = Column(LargeBinary, nullable=False)  # Serialized vector embedding
    model = Column(String, nullable=False)  # Model used to generate embedding
    provider = Column(String, nullable=False)  # Provider used ('openai', 'local', etc.)
    created_at = Column(Integer, nullable=False)
    
    # Composite index for efficient lookups
    __table_args__ = (
        Index('idx_content_embedding_lookup', 'content_id', 'content_type', 'collection_id'),
        Index('idx_content_embedding_collection', 'collection_id'),
    )


class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_session_id = Column(String, ForeignKey('analysis_sessions.id'), nullable=False)
    created_at = Column(Integer, nullable=False)
    last_active = Column(Integer, nullable=False)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="chat_session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_session_id = Column(String, ForeignKey('chat_sessions.id'), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(Integer, nullable=False)
    provider_used = Column(String)  # Which LLM provider was used (for assistant messages)
    model_used = Column(String)  # Which model was used (for assistant messages)
    tokens_used = Column(Integer, default=0)
    cost_estimate = Column(Float, default=0.0)
    
    # Relationship
    chat_session = relationship("ChatSession", back_populates="messages")


# Indexes for performance optimization
Index('idx_keyword_mentions_session', KeywordMention.analysis_session_id)
Index('idx_keyword_mentions_keyword', KeywordMention.keyword)
Index('idx_keyword_mentions_date', KeywordMention.created_utc)
Index('idx_keyword_mentions_filtering', KeywordMention.analysis_session_id, KeywordMention.keyword, KeywordMention.sentiment_score, KeywordMention.created_utc)
Index('idx_keyword_stats_session', KeywordStat.analysis_session_id)
Index('idx_cooccurrences_session', KeywordCooccurrence.analysis_session_id)
Index('idx_chat_messages_session', ChatMessage.chat_session_id)
Index('idx_chat_messages_timestamp', ChatMessage.timestamp)


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
    
    # Phase 1: Collection Methods (existing - unchanged)
    
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
    
    # Phase 2: Analytics Methods (existing - unchanged)
    
    def create_analysis_session(self, name: str, keywords: List[str], collection_ids: List[str],
                               partial_matching: bool = False, context_window_words: int = 20) -> str:
        """Create a new analysis session and return its ID."""
        session = self.get_session()
        try:
            analysis_session = AnalysisSession(
                name=name,
                keywords=json.dumps(keywords),
                collection_ids=json.dumps(collection_ids),
                created_at=int(datetime.utcnow().timestamp()),
                partial_matching=partial_matching,
                context_window_words=context_window_words
            )
            session.add(analysis_session)
            session.commit()
            return analysis_session.id
        finally:
            session.close()
    
    def update_analysis_session_status(self, session_id: str, status: str):
        """Update the status of an analysis session."""
        session = self.get_session()
        try:
            analysis_session = session.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
            if analysis_session:
                analysis_session.status = status
                session.commit()
        finally:
            session.close()
    
    def update_analysis_session_stats(self, session_id: str, total_mentions: int, avg_sentiment: float):
        """Update overall statistics for an analysis session."""
        session = self.get_session()
        try:
            analysis_session = session.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
            if analysis_session:
                analysis_session.total_mentions = total_mentions
                analysis_session.avg_sentiment = avg_sentiment
                session.commit()
        finally:
            session.close()
    
    def get_analysis_sessions(self) -> List[AnalysisSession]:
        """Get all analysis sessions."""
        session = self.get_session()
        try:
            return session.query(AnalysisSession).order_by(AnalysisSession.created_at.desc()).all()
        finally:
            session.close()
    
    def get_analysis_session(self, session_id: str) -> Optional[AnalysisSession]:
        """Get a specific analysis session."""
        session = self.get_session()
        try:
            return session.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        finally:
            session.close()
    
    def delete_analysis_session(self, session_id: str):
        """Delete an analysis session and all related data."""
        session = self.get_session()
        try:
            analysis_session = session.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
            if analysis_session:
                session.delete(analysis_session)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    # Phase 3: LLM Methods (new)
    
    def save_llm_summary(self, session_id: str, user_query: str, summary_text: str,
                        provider_used: str, model_used: str, tokens_used: int, cost_estimate: float):
        """Save an LLM-generated summary for an analysis session."""
        session = self.get_session()
        try:
            llm_summary = LLMSummary(
                analysis_session_id=session_id,
                user_query=user_query,
                summary_text=summary_text,
                generated_at=int(datetime.utcnow().timestamp()),
                provider_used=provider_used,
                model_used=model_used,
                tokens_used=tokens_used,
                cost_estimate=cost_estimate
            )
            session.merge(llm_summary)  # Use merge to handle updates
            session.commit()
        finally:
            session.close()
    
    def get_llm_summary(self, session_id: str) -> Optional[LLMSummary]:
        """Get LLM summary for an analysis session."""
        session = self.get_session()
        try:
            return session.query(LLMSummary).filter(LLMSummary.analysis_session_id == session_id).first()
        finally:
            session.close()
    
    def create_chat_session(self, analysis_session_id: str) -> str:
        """Create a new chat session and return its ID."""
        session = self.get_session()
        try:
            chat_session = ChatSession(
                analysis_session_id=analysis_session_id,
                created_at=int(datetime.utcnow().timestamp()),
                last_active=int(datetime.utcnow().timestamp())
            )
            session.add(chat_session)
            session.commit()
            return chat_session.id
        finally:
            session.close()
    
    def save_chat_message(self, chat_session_id: str, role: str, content: str,
                         provider_used: str = None, model_used: str = None,
                         tokens_used: int = 0, cost_estimate: float = 0.0):
        """Save a chat message."""
        session = self.get_session()
        try:
            message = ChatMessage(
                chat_session_id=chat_session_id,
                role=role,
                content=content,
                timestamp=int(datetime.utcnow().timestamp()),
                provider_used=provider_used,
                model_used=model_used,
                tokens_used=tokens_used,
                cost_estimate=cost_estimate
            )
            session.add(message)
            
            # Update chat session last_active
            chat_session = session.query(ChatSession).filter(ChatSession.id == chat_session_id).first()
            if chat_session:
                chat_session.last_active = int(datetime.utcnow().timestamp())
            
            session.commit()
        finally:
            session.close()
    
    def get_chat_sessions(self, analysis_session_id: str) -> List[ChatSession]:
        """Get chat sessions for an analysis session."""
        session = self.get_session()
        try:
            return session.query(ChatSession).filter(
                ChatSession.analysis_session_id == analysis_session_id
            ).order_by(ChatSession.last_active.desc()).all()
        finally:
            session.close()
    
    def get_chat_messages(self, chat_session_id: str, limit: int = 50) -> List[ChatMessage]:
        """Get messages for a chat session."""
        session = self.get_session()
        try:
            return session.query(ChatMessage).filter(
                ChatMessage.chat_session_id == chat_session_id
            ).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
        finally:
            session.close()


# Global database instance
db = Database()
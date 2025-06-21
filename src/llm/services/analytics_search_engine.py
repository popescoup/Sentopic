"""
Analytics Search Engine

Bridge between analytics data and discussion retrieval. Enables precision targeting
of discussions based on analytical findings rather than broad text search.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy import func, desc, and_
import json

from ...database import db, Post, Comment, KeywordMention, KeywordStat, KeywordCooccurrence
from .discussion_builder import discussion_builder
from .content_formatter import content_formatter


@dataclass
class AnalyticsSearchResult:
    """Search result that combines analytics insights with discussion context."""
    content_id: str                    # Reddit ID of post/comment
    content_type: str                  # 'post' or 'comment'
    collection_id: str                 # Collection this content belongs to
    keyword: str                       # The keyword that was found
    mention_context: str               # Text context around the keyword mention
    sentiment_score: float             # Sentiment of this specific mention
    analytics_metadata: Dict[str, Any] # Rich analytics context
    discussion_context: Optional[Dict[str, Any]] = None  # Full discussion thread


class AnalyticsSearchEngine:
    """
    Search engine that leverages your existing analytics data to find
    precise, contextually relevant discussions based on analytical insights.
    """
    
    def __init__(self):
        pass
    
    def search_by_keyword_analytics(self, keyword: str, collection_ids: List[str], 
                                  limit: int = 10) -> List[AnalyticsSearchResult]:
        """
        Search for discussions using analytics data for a specific keyword.
        
        Args:
            keyword: Keyword to search for (must match your analyzed keywords)
            collection_ids: Collection IDs to search within
            limit: Maximum results to return
        
        Returns:
            List of analytics-informed search results
        """
        session = db.get_session()
        try:
            results = []
            
            # FIXED: Get analysis sessions that analyzed these collections
            analysis_session_ids = self._get_analysis_sessions_for_collections(collection_ids, session)
            
            if not analysis_session_ids:
                return results
            
            # Get keyword statistics for these analysis sessions
            keyword_stats = session.query(KeywordStat).filter(
                KeywordStat.keyword == keyword,
                KeywordStat.analysis_session_id.in_(analysis_session_ids)  # FIXED: Use analysis_session_id
            ).all()
            
            if not keyword_stats:
                return results  # Keyword not found in analytics
            
            # Get specific mentions of this keyword, ordered by relevance
            mentions = session.query(KeywordMention).filter(
                KeywordMention.keyword == keyword,
                KeywordMention.analysis_session_id.in_(analysis_session_ids),  # FIXED: Use analysis_session_id
                KeywordMention.collection_id.in_(collection_ids)
            ).order_by(
                desc(KeywordMention.sentiment_score),  # Prioritize high sentiment
                func.random()                          # Then random for diversity
            ).limit(limit * 2).all()  # Get more to filter from
            
            # Convert mentions to search results with full context
            for mention in mentions[:limit]:
                # Build analytics metadata
                stats_for_session = next(
                    (stat for stat in keyword_stats if stat.analysis_session_id == mention.analysis_session_id),
                    None
                )
                
                analytics_metadata = self._build_analytics_metadata(
                    keyword, mention, stats_for_session, session
                )
                
                # Get surrounding context text
                context_text = self._extract_mention_context(mention, session)
                
                result = AnalyticsSearchResult(
                    content_id=mention.content_reddit_id,
                    content_type=mention.content_type,
                    collection_id=mention.collection_id,
                    keyword=keyword,
                    mention_context=context_text,
                    sentiment_score=mention.sentiment_score,
                    analytics_metadata=analytics_metadata
                )
                
                results.append(result)
            
            return results
            
        finally:
            session.close()
    
    def get_keyword_overview(self, keyword: str, collection_ids: List[str]) -> Dict[str, Any]:
        """
        Get comprehensive analytics overview for a keyword.
        
        Args:
            keyword: Keyword to analyze
            collection_ids: Collection IDs to include
        
        Returns:
            Comprehensive keyword analytics
        """
        session = db.get_session()
        try:
            # FIXED: Get analysis sessions that analyzed these collections
            analysis_session_ids = self._get_analysis_sessions_for_collections(collection_ids, session)
            
            if not analysis_session_ids:
                return {'found': False, 'keyword': keyword}
            
            # Get keyword statistics across analysis sessions
            keyword_stats = session.query(KeywordStat).filter(
                KeywordStat.keyword == keyword,
                KeywordStat.analysis_session_id.in_(analysis_session_ids)  # FIXED: Use analysis_session_id
            ).all()
            
            if not keyword_stats:
                return {'found': False, 'keyword': keyword}
            
            # FIXED: Filter stats to only include those that analyzed the target collections
            relevant_stats = []
            for stat in keyword_stats:
                collections_found_in = json.loads(stat.collections_found_in)
                if any(collection_id in collections_found_in for collection_id in collection_ids):
                    relevant_stats.append(stat)
            
            if not relevant_stats:
                return {'found': False, 'keyword': keyword}
            
            # Aggregate statistics
            total_mentions = sum(stat.total_mentions for stat in relevant_stats)
            avg_sentiment = sum(stat.avg_sentiment * stat.total_mentions for stat in relevant_stats) / total_mentions if total_mentions > 0 else 0
            
            # Get mention distribution
            mention_counts = session.query(
                KeywordMention.content_type,
                func.count(KeywordMention.id).label('count')
            ).filter(
                KeywordMention.keyword == keyword,
                KeywordMention.analysis_session_id.in_(analysis_session_ids),  # FIXED: Use analysis_session_id
                KeywordMention.collection_id.in_(collection_ids)
            ).group_by(KeywordMention.content_type).all()
            
            # Get sentiment distribution
            sentiment_ranges = {
                'very_positive': 0, 'positive': 0, 'neutral': 0, 'negative': 0, 'very_negative': 0
            }
            
            mentions = session.query(KeywordMention.sentiment_score).filter(
                KeywordMention.keyword == keyword,
                KeywordMention.analysis_session_id.in_(analysis_session_ids),  # FIXED: Use analysis_session_id
                KeywordMention.collection_id.in_(collection_ids)
            ).all()
            
            for mention in mentions:
                score = mention.sentiment_score
                if score >= 0.6:
                    sentiment_ranges['very_positive'] += 1
                elif score >= 0.2:
                    sentiment_ranges['positive'] += 1
                elif score >= -0.2:
                    sentiment_ranges['neutral'] += 1
                elif score >= -0.6:
                    sentiment_ranges['negative'] += 1
                else:
                    sentiment_ranges['very_negative'] += 1
            
            # Get top co-occurring keywords
            cooccurrences = session.query(KeywordCooccurrence).filter(
                and_(
                    KeywordCooccurrence.keyword1 == keyword,
                    KeywordCooccurrence.analysis_session_id.in_(analysis_session_ids)  # FIXED: Use analysis_session_id
                )
            ).order_by(desc(KeywordCooccurrence.cooccurrence_count)).limit(5).all()
            
            return {
                'found': True,
                'keyword': keyword,
                'total_mentions': total_mentions,
                'avg_sentiment': avg_sentiment,
                'collections_found': len(relevant_stats),
                'mention_distribution': {row.content_type: row.count for row in mention_counts},
                'sentiment_distribution': sentiment_ranges,
                'top_cooccurrences': [
                    {
                        'keyword': co.keyword2,
                        'count': co.cooccurrence_count,
                        'in_posts': co.in_posts,
                        'in_comments': co.in_comments
                    }
                    for co in cooccurrences
                ],
                'collections_detail': [
                    {
                        'analysis_session_id': stat.analysis_session_id,
                        'mentions': stat.total_mentions,
                        'sentiment': stat.avg_sentiment,
                        'collections_analyzed': json.loads(stat.collections_found_in)
                    }
                    for stat in relevant_stats
                ]
            }
            
        finally:
            session.close()
    
    def search_by_analytics_insights(self, collection_ids: List[str], 
                                   insight_type: str = 'most_frequent',
                                   limit: int = 5) -> List[AnalyticsSearchResult]:
        """
        Search based on analytics insights (most frequent, most positive, etc.)
        
        Args:
            collection_ids: Collection IDs to search within
            insight_type: 'most_frequent', 'most_positive', 'most_negative', 'trending'
            limit: Maximum results to return
        
        Returns:
            List of analytics-driven search results
        """
        session = db.get_session()
        try:
            results = []
            
            # FIXED: Get analysis sessions that analyzed these collections
            analysis_session_ids = self._get_analysis_sessions_for_collections(collection_ids, session)
            
            if not analysis_session_ids:
                return results
            
            # Get keywords based on insight type
            if insight_type == 'most_frequent':
                top_keywords = session.query(KeywordStat.keyword).filter(
                    KeywordStat.analysis_session_id.in_(analysis_session_ids)  # FIXED: Use analysis_session_id
                ).order_by(desc(KeywordStat.total_mentions)).limit(limit).all()
            
            elif insight_type == 'most_positive':
                top_keywords = session.query(KeywordStat.keyword).filter(
                    KeywordStat.analysis_session_id.in_(analysis_session_ids),  # FIXED: Use analysis_session_id
                    KeywordStat.avg_sentiment > 0.2
                ).order_by(desc(KeywordStat.avg_sentiment)).limit(limit).all()
            
            elif insight_type == 'most_negative':
                top_keywords = session.query(KeywordStat.keyword).filter(
                    KeywordStat.analysis_session_id.in_(analysis_session_ids),  # FIXED: Use analysis_session_id
                    KeywordStat.avg_sentiment < -0.2
                ).order_by(KeywordStat.avg_sentiment).limit(limit).all()
            
            else:  # Default to most frequent
                top_keywords = session.query(KeywordStat.keyword).filter(
                    KeywordStat.analysis_session_id.in_(analysis_session_ids)  # FIXED: Use analysis_session_id
                ).order_by(desc(KeywordStat.total_mentions)).limit(limit).all()
            
            # Get representative examples for each keyword
            for keyword_row in top_keywords:
                keyword = keyword_row.keyword
                keyword_results = self.search_by_keyword_analytics(
                    keyword, collection_ids, limit=2
                )
                results.extend(keyword_results)
            
            return results
            
        finally:
            session.close()
    
    def find_discussions_with_multiple_keywords(self, keywords: List[str], 
                                              collection_ids: List[str],
                                              limit: int = 10) -> List[AnalyticsSearchResult]:
        """
        Find discussions that contain multiple keywords from your analysis.
        
        Args:
            keywords: List of keywords to find together
            collection_ids: Collection IDs to search within
            limit: Maximum results to return
        
        Returns:
            Discussions containing multiple target keywords
        """
        session = db.get_session()
        try:
            results = []
            
            if len(keywords) < 2:
                return results
            
            # FIXED: Get analysis sessions that analyzed these collections
            analysis_session_ids = self._get_analysis_sessions_for_collections(collection_ids, session)
            
            if not analysis_session_ids:
                return results
            
            # Find content that has mentions of multiple keywords
            keyword_mentions = {}
            for keyword in keywords:
                mentions = session.query(KeywordMention).filter(
                    KeywordMention.keyword == keyword,
                    KeywordMention.analysis_session_id.in_(analysis_session_ids),  # FIXED: Use analysis_session_id
                    KeywordMention.collection_id.in_(collection_ids)
                ).all()
                
                for mention in mentions:
                    content_key = (mention.content_reddit_id, mention.content_type, mention.collection_id)
                    if content_key not in keyword_mentions:
                        keyword_mentions[content_key] = []
                    keyword_mentions[content_key].append(mention)
            
            # Find content with multiple keyword matches
            multi_keyword_content = [
                (content_key, mentions) for content_key, mentions in keyword_mentions.items()
                if len(set(m.keyword for m in mentions)) >= 2
            ]
            
            # Sort by number of keyword matches and sentiment
            multi_keyword_content.sort(
                key=lambda x: (len(set(m.keyword for m in x[1])), 
                              sum(m.sentiment_score for m in x[1]) / len(x[1])),
                reverse=True
            )
            
            # Convert to search results
            for (content_id, content_type, collection_id), mentions in multi_keyword_content[:limit]:
                # Use the mention with the highest sentiment as primary
                primary_mention = max(mentions, key=lambda m: m.sentiment_score)
                
                # Build analytics metadata for multi-keyword context
                analytics_metadata = {
                    'primary_keyword': primary_mention.keyword,
                    'all_keywords_found': list(set(m.keyword for m in mentions)),
                    'keyword_count': len(set(m.keyword for m in mentions)),
                    'avg_sentiment_all_keywords': sum(m.sentiment_score for m in mentions) / len(mentions),
                    'mention_details': [
                        {
                            'keyword': m.keyword,
                            'sentiment': m.sentiment_score,
                            'position': m.position_in_content
                        }
                        for m in mentions
                    ]
                }
                
                context_text = self._extract_mention_context(primary_mention, session)
                
                result = AnalyticsSearchResult(
                    content_id=content_id,
                    content_type=content_type,
                    collection_id=collection_id,
                    keyword=primary_mention.keyword,
                    mention_context=context_text,
                    sentiment_score=primary_mention.sentiment_score,
                    analytics_metadata=analytics_metadata
                )
                
                results.append(result)
            
            return results
            
        finally:
            session.close()
    
    def _get_analysis_sessions_for_collections(self, collection_ids: List[str], session) -> List[str]:
        """
        FIXED: Get analysis session IDs that analyzed the given collections.
        
        Args:
            collection_ids: Collection IDs to find analysis sessions for
            session: Database session
        
        Returns:
            List of analysis session IDs
        """
        from ...database import AnalysisSession
        
        # Get all analysis sessions
        analysis_sessions = session.query(AnalysisSession).all()
        
        matching_session_ids = []
        for analysis_session in analysis_sessions:
            session_collection_ids = json.loads(analysis_session.collection_ids)
            # Check if any of the target collections were analyzed in this session
            if any(collection_id in session_collection_ids for collection_id in collection_ids):
                matching_session_ids.append(analysis_session.id)
        
        return matching_session_ids
    
    def _build_analytics_metadata(self, keyword: str, mention: KeywordMention, 
                                keyword_stat: Optional[KeywordStat], session) -> Dict[str, Any]:
        """Build rich analytics metadata for a search result."""
        metadata = {
            'keyword': keyword,
            'mention_sentiment': mention.sentiment_score,
            'mention_position': mention.position_in_content,
            'content_type': mention.content_type
        }
        
        # Add keyword statistics if available
        if keyword_stat:
            metadata.update({
                'keyword_total_mentions': keyword_stat.total_mentions,
                'keyword_avg_sentiment': keyword_stat.avg_sentiment,
                'keyword_frequency_rank': self._get_keyword_rank(keyword, keyword_stat.analysis_session_id, session)
            })
        
        # Add content metadata
        if mention.content_type == 'post':
            post = session.query(Post).filter(
                Post.reddit_id == mention.content_reddit_id,
                Post.collection_id == mention.collection_id
            ).first()
            
            if post:
                metadata.update({
                    'post_title': post.title,
                    'post_score': post.score,
                    'post_author': post.author,
                    'subreddit': post.subreddit
                })
        
        else:  # comment
            comment = session.query(Comment).filter(
                Comment.reddit_id == mention.content_reddit_id,
                Comment.collection_id == mention.collection_id
            ).first()
            
            if comment:
                metadata.update({
                    'comment_score': comment.score,
                    'comment_author': comment.author,
                    'comment_depth': comment.depth,
                    'is_root_comment': comment.is_root
                })
        
        return metadata
    
    def _extract_mention_context(self, mention: KeywordMention, session, 
                               context_chars: int = 200) -> str:
        """Extract text context around a keyword mention."""
        # Get the full content
        if mention.content_type == 'post':
            post = session.query(Post).filter(
                Post.reddit_id == mention.content_reddit_id,
                Post.collection_id == mention.collection_id
            ).first()
            
            if post:
                full_text = (post.title or '') + ' ' + (post.content or '')
            else:
                return ""
        
        else:  # comment
            comment = session.query(Comment).filter(
                Comment.reddit_id == mention.content_reddit_id,
                Comment.collection_id == mention.collection_id
            ).first()
            
            if comment:
                full_text = comment.content or ''
            else:
                return ""
        
        # Extract context around the mention position
        if not full_text or mention.position_in_content < 0:
            return full_text[:context_chars] + "..." if len(full_text) > context_chars else full_text
        
        # Get context around the position
        start = max(0, mention.position_in_content - context_chars // 2)
        end = min(len(full_text), mention.position_in_content + len(mention.keyword) + context_chars // 2)
        
        context = full_text[start:end]
        
        # Add ellipsis if truncated
        if start > 0:
            context = "..." + context
        if end < len(full_text):
            context = context + "..."
        
        return context
    
    def _get_keyword_rank(self, keyword: str, analysis_session_id: str, session) -> int:
        """Get the frequency rank of a keyword within an analysis session."""
        try:
            # Count keywords with higher mention counts in the same analysis session
            higher_count = session.query(func.count(KeywordStat.keyword)).filter(
                KeywordStat.analysis_session_id == analysis_session_id,
                KeywordStat.total_mentions > (
                    session.query(KeywordStat.total_mentions).filter(
                        KeywordStat.keyword == keyword,
                        KeywordStat.analysis_session_id == analysis_session_id
                    ).scalar()
                )
            ).scalar()
            
            return higher_count + 1  # Rank is 1-based
        except:
            return 0
    
    def enrich_with_discussion_context(self, results: List[AnalyticsSearchResult]) -> List[AnalyticsSearchResult]:
        """
        Enrich analytics search results with full discussion contexts.
        
        Args:
            results: List of analytics search results
        
        Returns:
            Results enriched with complete discussion threads
        """
        for result in results:
            try:
                if result.content_type == 'post':
                    discussion = discussion_builder.build_discussion_from_post(
                        result.content_id, result.collection_id
                    )
                else:
                    discussion = discussion_builder.build_discussion_from_comment(
                        result.content_id, result.collection_id
                    )
                
                result.discussion_context = discussion
            except Exception:
                # Continue if individual discussion building fails
                continue
        
        return results


# Global analytics search engine instance
analytics_search_engine = AnalyticsSearchEngine()
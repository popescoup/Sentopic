"""
Enhanced Analytics Search Engine

Analytics search with graceful handling of keywords not found in analysis data.
Provides helpful suggestions and maintains functionality even when exact matches aren't available.
"""

from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from sqlalchemy import func, desc, and_
import json
import difflib

from ...database import db, Post, Comment, KeywordMention, KeywordStat, KeywordCooccurrence
from .discussion_builder import discussion_builder
from .content_formatter import content_formatter
from dataclasses import dataclass


@dataclass
class AnalyticsSearchResult:
    """Enhanced search result with additional context and suggestions."""
    content_id: str                    # Reddit ID of post/comment
    content_type: str                  # 'post' or 'comment'
    collection_id: str                 # Collection this content belongs to
    keyword: str                       # The keyword that was found
    mention_context: str               # Text context around the keyword mention
    sentiment_score: float             # Sentiment of this specific mention
    analytics_metadata: Dict[str, Any] # Rich analytics context
    discussion_context: Optional[Dict[str, Any]] = None  # Full discussion thread
    search_notes: Optional[str] = None  # Notes about search method used


class AnalyticsSearchEngine:
    """
    Enhanced analytics search engine with graceful keyword handling and intelligent suggestions.
    
    Key improvements:
    - Graceful handling when keywords aren't found in analysis data
    - Fuzzy matching and suggestions for similar keywords
    - Enhanced error messages with helpful alternatives
    - Maintained functionality even with incomplete analytics data
    """
    
    def __init__(self):
        pass
    
    def search_by_keyword_analytics(self, keyword: str, collection_ids: List[str], 
                                  limit: int = 10) -> List[AnalyticsSearchResult]:
        """
        Enhanced search for discussions using analytics data with graceful fallbacks.
        
        Args:
            keyword: Keyword to search for (supports fuzzy matching)
            collection_ids: Collection IDs to search within
            limit: Maximum results to return
        
        Returns:
            List of analytics-informed search results with helpful context
        """
        session = db.get_session()
        try:
            results = []
            
            # Get analysis sessions that analyzed these collections
            analysis_session_ids = self._get_analysis_sessions_for_collections(collection_ids, session)
            
            if not analysis_session_ids:
                return self._create_fallback_results(keyword, collection_ids, limit, "no_analysis_sessions")
            
            # Try exact keyword match first
            keyword_stats = session.query(KeywordStat).filter(
                KeywordStat.keyword == keyword,
                KeywordStat.analysis_session_id.in_(analysis_session_ids)
            ).all()
            
            if keyword_stats:
                # Found exact match - proceed with normal analytics search
                return self._perform_analytics_search(keyword, analysis_session_ids, collection_ids, limit, session)
            
            else:
                # No exact match - try fuzzy matching and suggestions
                return self._handle_no_exact_match(keyword, analysis_session_ids, collection_ids, limit, session)
            
        finally:
            session.close()
    
    def get_keyword_overview(self, keyword: str, collection_ids: List[str], 
                            analysis_session_id: str = None) -> Dict[str, Any]:
        """
        Enhanced keyword overview with suggestions when keyword not found.
    
        Args:
            keyword: Keyword to analyze
            collection_ids: Collection IDs to include
            analysis_session_id: Specific analysis session ID to use (optional)
    
        Returns:
            Comprehensive keyword analytics with suggestions if not found
        """
        session = db.get_session()
        try:
            # Get analysis sessions that analyzed these collections
            if analysis_session_id:
                analysis_session_ids = [analysis_session_id]
            else:
                analysis_session_ids = self._get_analysis_sessions_for_collections(collection_ids, session)
            
            if not analysis_session_ids:
                return {
                    'found': False, 
                    'keyword': keyword,
                    'reason': 'no_analysis_sessions',
                    'message': 'No analysis sessions found for the specified collections.',
                    'suggestions': []
                }
            
            # Try exact match
            keyword_stats = session.query(KeywordStat).filter(
                KeywordStat.keyword == keyword,
                KeywordStat.analysis_session_id.in_(analysis_session_ids)
            ).all()
            
            if keyword_stats:
                # Found exact match - return full analytics
                return self._build_full_keyword_overview(keyword, keyword_stats, collection_ids, session)
            
            else:
                # No exact match - provide helpful response with suggestions
                return self._build_keyword_not_found_response(keyword, analysis_session_ids, collection_ids, session)
            
        finally:
            session.close()
    
    def _perform_analytics_search(self, keyword: str, analysis_session_ids: List[str], 
                                collection_ids: List[str], limit: int, session) -> List[AnalyticsSearchResult]:
        """Perform normal analytics search when keyword is found."""
        results = []
        
        # Get specific mentions of this keyword, ordered by relevance
        mentions = session.query(KeywordMention).filter(
            KeywordMention.keyword == keyword,
            KeywordMention.analysis_session_id.in_(analysis_session_ids),
            KeywordMention.collection_id.in_(collection_ids)
        ).order_by(
            desc(KeywordMention.sentiment_score),  # Prioritize high sentiment
            func.random()                          # Then random for diversity
        ).limit(limit * 2).all()  # Get more to filter from
        
        # Convert mentions to search results with full context
        for mention in mentions[:limit]:
            # Build analytics metadata
            stats_for_session = session.query(KeywordStat).filter(
                KeywordStat.keyword == keyword,
                KeywordStat.analysis_session_id == mention.analysis_session_id
            ).first()
            
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
                analytics_metadata=analytics_metadata,
                search_notes=f"Found via analytics data: {mention.analysis_session_id}"
            )
            
            results.append(result)
        
        return results
    
    def _handle_no_exact_match(self, keyword: str, analysis_session_ids: List[str],
                             collection_ids: List[str], limit: int, session) -> List[AnalyticsSearchResult]:
        """Handle case where keyword is not found in analytics data."""
        # Get all available keywords for fuzzy matching
        all_keywords = session.query(KeywordStat.keyword).filter(
            KeywordStat.analysis_session_id.in_(analysis_session_ids)
        ).distinct().all()
        
        available_keywords = [kw.keyword for kw in all_keywords]
        
        # Try fuzzy matching
        similar_keywords = difflib.get_close_matches(keyword, available_keywords, n=3, cutoff=0.6)
        
        if similar_keywords:
            # Found similar keywords - search using the best match
            best_match = similar_keywords[0]
            results = self._perform_analytics_search(best_match, analysis_session_ids, collection_ids, limit, session)
            
            # Add search notes explaining the fuzzy match
            for result in results:
                result.search_notes = f"Fuzzy match: searched for '{best_match}' instead of '{keyword}'"
                result.keyword = keyword  # Keep original keyword in result
                if result.analytics_metadata:
                    result.analytics_metadata['original_keyword'] = keyword
                    result.analytics_metadata['matched_keyword'] = best_match
                    result.analytics_metadata['similarity_score'] = difflib.SequenceMatcher(None, keyword, best_match).ratio()
            
            return results
        
        else:
            # No similar keywords found - create fallback results
            return self._create_fallback_results(keyword, collection_ids, limit, "no_similar_keywords", available_keywords)
    
    def _create_fallback_results(self, keyword: str, collection_ids: List[str], 
                               limit: int, reason: str, available_keywords: List[str] = None) -> List[AnalyticsSearchResult]:
        """Create fallback results when analytics search isn't possible."""
        # This would typically be an empty list, but we can provide some helpful context
        # The RAG engine will handle the actual fallback search using other methods
        
        fallback_result = AnalyticsSearchResult(
            content_id="fallback",
            content_type="system_message",
            collection_id="system",
            keyword=keyword,
            mention_context=self._build_fallback_message(keyword, reason, available_keywords),
            sentiment_score=0.0,
            analytics_metadata={
                'fallback_reason': reason,
                'available_keywords': available_keywords[:10] if available_keywords else [],
                'total_available_keywords': len(available_keywords) if available_keywords else 0,
                'suggested_action': 'use_discussion_search'
            },
            search_notes=f"Keyword '{keyword}' not found in analytics data. Fallback to discussion search recommended."
        )
        
        return [fallback_result]
    
    def _build_fallback_message(self, keyword: str, reason: str, available_keywords: List[str] = None) -> str:
        """Build helpful fallback message when keyword not found."""
        if reason == "no_analysis_sessions":
            return f"No analysis data available for the specified collections. The keyword '{keyword}' cannot be found in formal analysis, but discussions may still be available."
        
        elif reason == "no_similar_keywords":
            message = f"The keyword '{keyword}' was not found in your analysis data."
            
            if available_keywords:
                # Suggest some available keywords
                suggestions = available_keywords[:5] if len(available_keywords) > 5 else available_keywords
                message += f" Available keywords include: {', '.join(suggestions)}"
                
                if len(available_keywords) > 5:
                    message += f" (and {len(available_keywords) - 5} more)"
                
                message += ". You can search for discussions about this topic using other search methods."
            else:
                message += " No keywords found in analysis data."
            
            return message
        
        else:
            return f"Unable to find analytics data for '{keyword}'. Reason: {reason}"
    
    def _build_full_keyword_overview(self, keyword: str, keyword_stats: List[KeywordStat],
                                   collection_ids: List[str], session) -> Dict[str, Any]:
        """Build full keyword overview when keyword is found in analytics."""
        # Filter stats to only include those that analyzed the target collections
        relevant_stats = []
        for stat in keyword_stats:
            collections_found_in = json.loads(stat.collections_found_in)
            if any(collection_id in collections_found_in for collection_id in collection_ids):
                relevant_stats.append(stat)
        
        if not relevant_stats:
            return {
                'found': False,
                'keyword': keyword,
                'reason': 'not_in_target_collections',
                'message': f"Keyword '{keyword}' exists in analysis data but not for the specified collections.",
                'suggestions': []
            }
        
        # Aggregate statistics
        total_mentions = sum(stat.total_mentions for stat in relevant_stats)
        avg_sentiment = sum(stat.avg_sentiment * stat.total_mentions for stat in relevant_stats) / total_mentions if total_mentions > 0 else 0
        
        # Get mention distribution
        analysis_session_ids = [stat.analysis_session_id for stat in relevant_stats]
        mention_counts = session.query(
            KeywordMention.content_type,
            func.count(KeywordMention.id).label('count')
        ).filter(
            KeywordMention.keyword == keyword,
            KeywordMention.analysis_session_id.in_(analysis_session_ids),
            KeywordMention.collection_id.in_(collection_ids)
        ).group_by(KeywordMention.content_type).all()
        
        # Get sentiment distribution
        sentiment_ranges = {
            'very_positive': 0, 'positive': 0, 'neutral': 0, 'negative': 0, 'very_negative': 0
        }
        
        mentions = session.query(KeywordMention.sentiment_score).filter(
            KeywordMention.keyword == keyword,
            KeywordMention.analysis_session_id.in_(analysis_session_ids),
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
                KeywordCooccurrence.analysis_session_id.in_(analysis_session_ids)
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
    
    def _build_keyword_not_found_response(self, keyword: str, analysis_session_ids: List[str],
                                        collection_ids: List[str], session) -> Dict[str, Any]:
        """Build helpful response when keyword is not found with suggestions."""
        # Get all available keywords for suggestions
        all_keywords = session.query(KeywordStat.keyword).filter(
            KeywordStat.analysis_session_id.in_(analysis_session_ids)
        ).distinct().all()
        
        available_keywords = [kw.keyword for kw in all_keywords]
        
        # Generate suggestions using fuzzy matching
        suggestions = []
        if available_keywords:
            # Fuzzy matches
            fuzzy_matches = difflib.get_close_matches(keyword, available_keywords, n=5, cutoff=0.4)
            suggestions.extend(fuzzy_matches)
            
            # If no fuzzy matches, suggest some popular keywords
            if not fuzzy_matches:
                # Get top keywords by mentions
                top_keywords = session.query(KeywordStat.keyword, func.sum(KeywordStat.total_mentions).label('total')).filter(
                    KeywordStat.analysis_session_id.in_(analysis_session_ids)
                ).group_by(KeywordStat.keyword).order_by(desc('total')).limit(5).all()
                
                suggestions = [kw.keyword for kw in top_keywords]
        
        return {
            'found': False,
            'keyword': keyword,
            'reason': 'keyword_not_in_analysis',
            'message': f"The keyword '{keyword}' was not found in your analysis data.",
            'suggestions': suggestions,
            'total_available_keywords': len(available_keywords),
            'available_keywords_sample': available_keywords[:10] if available_keywords else [],
            'help_text': "You can search for discussions about this topic using discussion search methods, or try one of the suggested keywords from your analysis."
        }
    
    def search_by_analytics_insights(self, collection_ids: List[str], 
                                   insight_type: str = 'most_frequent',
                                   limit: int = 5) -> List[AnalyticsSearchResult]:
        """
        Enhanced search based on analytics insights with better error handling.
        
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
            
            # Get analysis sessions that analyzed these collections
            analysis_session_ids = self._get_analysis_sessions_for_collections(collection_ids, session)
            
            if not analysis_session_ids:
                # Return helpful fallback information
                fallback_result = AnalyticsSearchResult(
                    content_id="no_analysis",
                    content_type="system_message",
                    collection_id="system",
                    keyword="insights",
                    mention_context="No analysis sessions found for the specified collections. Unable to provide analytics insights.",
                    sentiment_score=0.0,
                    analytics_metadata={
                        'fallback_reason': 'no_analysis_sessions',
                        'insight_type': insight_type,
                        'suggested_action': 'run_analysis_first'
                    },
                    search_notes="No analytics data available. Run analysis on these collections first."
                )
                return [fallback_result]
            
            # Get keywords based on insight type
            if insight_type == 'most_frequent':
                top_keywords = session.query(KeywordStat.keyword).filter(
                    KeywordStat.analysis_session_id.in_(analysis_session_ids)
                ).order_by(desc(KeywordStat.total_mentions)).limit(limit).all()
            
            elif insight_type == 'most_positive':
                top_keywords = session.query(KeywordStat.keyword).filter(
                    KeywordStat.analysis_session_id.in_(analysis_session_ids),
                    KeywordStat.avg_sentiment > 0.2
                ).order_by(desc(KeywordStat.avg_sentiment)).limit(limit).all()
            
            elif insight_type == 'most_negative':
                top_keywords = session.query(KeywordStat.keyword).filter(
                    KeywordStat.analysis_session_id.in_(analysis_session_ids),
                    KeywordStat.avg_sentiment < -0.2
                ).order_by(KeywordStat.avg_sentiment).limit(limit).all()
            
            else:  # Default to most frequent
                top_keywords = session.query(KeywordStat.keyword).filter(
                    KeywordStat.analysis_session_id.in_(analysis_session_ids)
                ).order_by(desc(KeywordStat.total_mentions)).limit(limit).all()
            
            # Get representative examples for each keyword
            for keyword_row in top_keywords:
                keyword = keyword_row.keyword
                keyword_results = self.search_by_keyword_analytics(
                    keyword, collection_ids, limit=2
                )
                
                # Filter out any fallback results for this aggregation
                valid_results = [r for r in keyword_results if r.content_type != "system_message"]
                results.extend(valid_results)
            
            return results
            
        finally:
            session.close()
    
    def find_discussions_with_multiple_keywords(self, keywords: List[str], 
                                              collection_ids: List[str],
                                              limit: int = 10) -> List[AnalyticsSearchResult]:
        """
        Enhanced search for discussions containing multiple keywords with graceful handling.
        
        Args:
            keywords: List of keywords to find together
            collection_ids: Collection IDs to search within
            limit: Maximum results to return
        
        Returns:
            Discussions containing multiple target keywords with fallback info
        """
        session = db.get_session()
        try:
            results = []
            
            if len(keywords) < 2:
                return results
            
            # Get analysis sessions that analyzed these collections
            analysis_session_ids = self._get_analysis_sessions_for_collections(collection_ids, session)
            
            if not analysis_session_ids:
                return results
            
            # Find which keywords are actually available in the analysis
            available_keywords = session.query(KeywordStat.keyword).filter(
                KeywordStat.analysis_session_id.in_(analysis_session_ids)
            ).distinct().all()
            
            available_keyword_list = [kw.keyword for kw in available_keywords]
            
            # Filter to only use keywords that exist in analysis
            valid_keywords = [kw for kw in keywords if kw in available_keyword_list]
            missing_keywords = [kw for kw in keywords if kw not in available_keyword_list]
            
            if not valid_keywords:
                # None of the requested keywords are in the analysis
                fallback_result = AnalyticsSearchResult(
                    content_id="no_valid_keywords",
                    content_type="system_message",
                    collection_id="system",
                    keyword="multiple_keywords",
                    mention_context=f"None of the requested keywords ({', '.join(keywords)}) were found in analysis data.",
                    sentiment_score=0.0,
                    analytics_metadata={
                        'requested_keywords': keywords,
                        'missing_keywords': missing_keywords,
                        'available_keywords': available_keyword_list[:10],
                        'suggested_action': 'use_discussion_search'
                    },
                    search_notes="Multi-keyword search not possible with analytics data. Try discussion search instead."
                )
                return [fallback_result]
            
            # Find content that has mentions of multiple valid keywords
            keyword_mentions = {}
            for keyword in valid_keywords:
                mentions = session.query(KeywordMention).filter(
                    KeywordMention.keyword == keyword,
                    KeywordMention.analysis_session_id.in_(analysis_session_ids),
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
                    'requested_keywords': keywords,
                    'valid_keywords': valid_keywords,
                    'missing_keywords': missing_keywords,
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
                
                search_notes = f"Found {len(set(m.keyword for m in mentions))} of {len(keywords)} requested keywords"
                if missing_keywords:
                    search_notes += f". Missing: {', '.join(missing_keywords)}"
                
                result = AnalyticsSearchResult(
                    content_id=content_id,
                    content_type=content_type,
                    collection_id=collection_id,
                    keyword=primary_mention.keyword,
                    mention_context=context_text,
                    sentiment_score=primary_mention.sentiment_score,
                    analytics_metadata=analytics_metadata,
                    search_notes=search_notes
                )
                
                results.append(result)
            
            return results
            
        finally:
            session.close()

    def _get_parent_post_id(self, comment_id: str, collection_id: str) -> str:
        """Get the parent post ID for a comment to enable deduplication by discussion."""
        session = db.get_session()
        try:
            comment = session.query(Comment).filter(
                Comment.reddit_id == comment_id,
                Comment.collection_id == collection_id
            ).first()
            return comment.post_reddit_id if comment else comment_id
        except:
            return comment_id  # Fallback to comment_id if lookup fails
        finally:
            session.close()

    def _merge_keyword_info(self, existing_result: AnalyticsSearchResult, 
                        new_result: AnalyticsSearchResult) -> AnalyticsSearchResult:
        """
        Merge keyword information from duplicate results into a single result.
    
        Args:
            existing_result: The result we're keeping
            new_result: The duplicate result with additional keyword info
    
        Returns:
            Enhanced existing result with merged keyword information
        """
        # Update analytics metadata to include info from both results
        if existing_result.analytics_metadata:
            # Add additional keywords found
            existing_keywords = existing_result.analytics_metadata.get('keywords_found', [existing_result.keyword])
            if existing_result.keyword not in existing_keywords:
                existing_keywords.append(existing_result.keyword)
            if new_result.keyword not in existing_keywords:
                existing_keywords.append(new_result.keyword)
        
            existing_result.analytics_metadata['keywords_found'] = existing_keywords
            existing_result.analytics_metadata['multiple_keyword_matches'] = True
        
            # Update mention context to be more comprehensive if needed
            if len(new_result.mention_context) > len(existing_result.mention_context):
                existing_result.mention_context = new_result.mention_context
    
        return existing_result
    
    def _get_analysis_sessions_for_collections(self, collection_ids: List[str], session) -> List[str]:
        """
        Get analysis session IDs that analyzed the given collections.
        
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
        Deduplicates results that refer to the same underlying discussion.
    
        Args:
            results: List of analytics search results
    
        Returns:
            Deduplicated results enriched with complete discussion threads
        """
        processed_discussions = {}  # Track: (content_id, collection_id) -> enriched_result
        enriched_results = []
    
        for result in results:
            # Skip system messages
            if result.content_type == "system_message":
                enriched_results.append(result)
                continue
        
            # Create key for deduplication based on the underlying post
            if result.content_type == 'post':
                discussion_key = (result.content_id, result.collection_id)
            else:
                # For comments, we want to dedupe by the parent post
                discussion_key = (self._get_parent_post_id(result.content_id, result.collection_id), result.collection_id)
        
            # Check if we've already processed this discussion
            if discussion_key in processed_discussions:
                # Merge keyword information into existing result
                existing_result = processed_discussions[discussion_key]
                existing_result = self._merge_keyword_info(existing_result, result)
                continue
        
            # New discussion - enrich it
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
                processed_discussions[discussion_key] = result
                enriched_results.append(result)
            except Exception:
                # Continue if individual discussion building fails
                continue
    
        return enriched_results


# Global enhanced analytics search engine instance
analytics_search_engine = AnalyticsSearchEngine()
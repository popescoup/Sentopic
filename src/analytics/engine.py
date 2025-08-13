"""
Analytics Engine

Main orchestration class for Phase 2 analytics functionality.
Coordinates keyword analysis, sentiment analysis, co-occurrence tracking,
and trend analysis. Enhanced with Phase 3.3 summarization capabilities.
"""

import json
from typing import List, Dict, Any, Optional
from tqdm import tqdm
from collections import defaultdict

from ..database import db, Collection, Post, Comment, AnalysisSession, KeywordMention, KeywordStat, KeywordCooccurrence
from .keywords import keyword_processor
from .sentiment import sentiment_analyzer
from .cooccurrence import cooccurrence_detector
from .trends import trends_analyzer
from ..llm.services.summarizer import analysis_summarizer
from ..llm import is_llm_available


class AnalyticsEngine:
    def __init__(self):
        pass
    
    def create_session(self, name: str, keywords: List[str], collection_ids: List[str],
                      partial_matching: bool = False, context_window_words: int = 5) -> str:
        """
        Create a new analysis session.
        
        Args:
            name: User-friendly name for the session
            keywords: List of keywords to search for
            collection_ids: List of collection IDs to analyze
            partial_matching: If True, use partial keyword matching
            context_window_words: Words to include before/after keyword for sentiment
        
        Returns:
            Session ID of the created session
        """
        # Validate inputs
        if not name.strip():
            raise ValueError("Session name cannot be empty")
        
        if not keywords:
            raise ValueError("At least one keyword is required")
        
        if not collection_ids:
            raise ValueError("At least one collection must be selected")
        
        # Clean keywords (remove empty strings and duplicates)
        keywords = list(set(k.strip() for k in keywords if k.strip()))
        
        if not keywords:
            raise ValueError("No valid keywords provided")
        
        # Validate collections exist
        session = db.get_session()
        try:
            existing_collections = session.query(Collection.id).filter(
                Collection.id.in_(collection_ids)
            ).all()
            existing_ids = [c.id for c in existing_collections]
            
            missing_collections = set(collection_ids) - set(existing_ids)
            if missing_collections:
                raise ValueError(f"Collections not found: {missing_collections}")
        finally:
            session.close()
        
        # Create analysis session
        session_id = db.create_analysis_session(
            name=name,
            keywords=keywords,
            collection_ids=collection_ids,
            partial_matching=partial_matching,
            context_window_words=context_window_words
        )
        
        return session_id
    
    def run_analysis(self, session_id: str) -> Dict[str, Any]:
        """
        Run complete analysis for a session.
        
        Args:
            session_id: Session ID to analyze
        
        Returns:
            Dictionary with analysis results summary
        """
        # Get session details
        analysis_session = db.get_analysis_session(session_id)
        if not analysis_session:
            raise ValueError(f"Analysis session not found: {session_id}")
        
        keywords = json.loads(analysis_session.keywords)
        collection_ids = json.loads(analysis_session.collection_ids)
        
        print(f"Starting analysis: {analysis_session.name}")
        print(f"Keywords: {', '.join(keywords)}")
        print(f"Collections: {len(collection_ids)}")
        print(f"Matching: {'Partial' if analysis_session.partial_matching else 'Exact'}")
        print(f"Context window: {analysis_session.context_window_words} words")
        print()
        
        try:
            # Set status to running when analysis starts
            db.update_analysis_session_status(session_id, 'running')

            # Process each collection
            all_keyword_mentions = []
            all_posts = []
            all_comments = []
            
            with tqdm(total=len(collection_ids), desc="Processing collections", unit="collection") as pbar:
                for collection_id in collection_ids:
                    # Get posts and comments for this collection
                    posts, comments = self._get_collection_content(collection_id)
                    all_posts.extend(posts)
                    all_comments.extend(comments)
                    
                    # Process keywords in posts and comments
                    post_matches = keyword_processor.process_posts_for_keywords(
                        posts, keywords, analysis_session.partial_matching
                    )
                    comment_matches = keyword_processor.process_comments_for_keywords(
                        comments, keywords, analysis_session.partial_matching
                    )
                    
                    # Analyze sentiment for each match
                    for match in post_matches + comment_matches:
                        context, sentiment = sentiment_analyzer.analyze_keyword_sentiment(
                            match['full_text'],
                            match['keyword'],
                            match['position'],
                            analysis_session.context_window_words
                        )
                        
                        all_keyword_mentions.append({
                            'analysis_session_id': session_id,
                            'keyword': match['keyword'],
                            'content_type': match['content_type'],
                            'content_reddit_id': match['content_reddit_id'],
                            'collection_id': collection_id,
                            'sentiment_score': sentiment,
                            'created_utc': match['created_utc'],
                            'position_in_content': match['position']
                        })
                    
                    pbar.update(1)
            
            # Save keyword mentions in batches
            print("Saving keyword mentions...")
            self._save_keyword_mentions_batch(all_keyword_mentions)
            
            # Calculate keyword statistics
            print("Computing keyword statistics...")
            keyword_stats = self._calculate_keyword_stats(session_id, keywords)
            self._save_keyword_stats_batch(session_id, keyword_stats)
            
            # Calculate co-occurrences
            print("Computing co-occurrences...")
            cooccurrence_data = cooccurrence_detector.process_content_for_cooccurrences(
                all_posts, all_comments, keywords, analysis_session.partial_matching, all_keyword_mentions
            )

            # DEBUG: Check what co-occurrence data was generated
            print(f"🔍 Co-occurrence data processed: {len(cooccurrence_data.get('pairs', {}))} pairs found")
            for pair, stats in list(cooccurrence_data.get('pairs', {}).items())[:3]:
                print(f"    {pair}: {stats['total_count']} occurrences")

            self._save_cooccurrences_batch(session_id, cooccurrence_data)

            # DEBUG: Verify data was saved to database
            test_session = db.get_session()
            try:
                saved_count = test_session.query(KeywordCooccurrence).filter(
                    KeywordCooccurrence.analysis_session_id == session_id
                ).count()
                print(f"🔍 Co-occurrences saved to database: {saved_count}")
            finally:
                test_session.close()
            
            # Update session with overall statistics
            total_mentions = len(all_keyword_mentions)
            avg_sentiment = sum(m['sentiment_score'] for m in all_keyword_mentions) / total_mentions if total_mentions > 0 else 0.0
            
            db.update_analysis_session_stats(session_id, total_mentions, avg_sentiment)
            db.update_analysis_session_status(session_id, 'completed')
            
            print(f"\nAnalysis completed successfully!")
            print(f"Total mentions found: {total_mentions}")
            print(f"Average sentiment: {avg_sentiment:.4f}")
            
            return {
                'session_id': session_id,
                'total_mentions': total_mentions,
                'avg_sentiment': avg_sentiment,
                'keywords_analyzed': len(keywords),
                'collections_processed': len(collection_ids),
                'status': 'completed'
            }
        
        except Exception as e:
            db.update_analysis_session_status(session_id, 'failed')
            raise e
    
    def run_analysis_with_summary(self, session_id: str, user_query: str = None, 
                                  generate_summary: bool = False) -> Dict[str, Any]:
        """
        Run complete analysis for a session with optional summary generation.
        
        Args:
            session_id: Session ID to analyze
            user_query: Optional user's research description for better summaries
            generate_summary: Whether to generate AI summary after analysis
        
        Returns:
            Dictionary with analysis results and summary information
        """
        # Run the standard analysis first
        analysis_results = self.run_analysis(session_id)
        
        # Generate summary if requested and LLM is available
        summary_results = None
        if generate_summary:
            if not is_llm_available():
                print("⚠️  Warning: LLM not available. Skipping summary generation.")
                print("   Enable LLM features in config.json to use summaries.")
            else:
                try:
                    print("\n🤖 Generating AI summary...")
                    summary_results = analysis_summarizer.generate_summary(session_id, user_query)
                    print("✅ Summary generated successfully!")
                except Exception as e:
                    print(f"⚠️  Warning: Failed to generate summary: {e}")
                    print("   Analysis completed successfully, but summary generation failed.")
        
        # Combine results
        combined_results = analysis_results.copy()
        if summary_results:
            combined_results['summary'] = summary_results
        
        return combined_results

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get existing summary for an analysis session.
        
        Args:
            session_id: Session ID to get summary for
        
        Returns:
            Summary data or None if no summary exists
        """
        return analysis_summarizer.get_existing_summary(session_id)

    def regenerate_session_summary(self, session_id: str, user_query: str = None) -> Dict[str, Any]:
        """
        Regenerate summary for an existing analysis session.
        
        Args:
            session_id: Session ID to regenerate summary for
            user_query: Optional updated research description
        
        Returns:
            Dictionary with new summary results
        """
        if not is_llm_available():
            raise RuntimeError("LLM not available. Cannot generate summaries.")
        
        return analysis_summarizer.regenerate_summary(session_id, user_query)

    def get_session_results_with_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get comprehensive results for an analysis session including summary if available.
    
        Args:
            session_id: Session ID to get results for
    
        Returns:
            Dictionary with complete session results and summary
        """
        # Get standard session results
        results = self.get_session_results(session_id)
    
        # Add summary if available
        summary = self.get_session_summary(session_id)
        if summary:
            results['summary'] = summary
    
        # Add analysis insights for dashboard cards
        if results.get('status') == 'completed':
            # Get co-occurrence data (all pairs)
            session = db.get_session()
            try:
                cooccurrences = session.query(KeywordCooccurrence).filter(
                    KeywordCooccurrence.analysis_session_id == session_id
                ).order_by(KeywordCooccurrence.cooccurrence_count.desc()).all()

                # DEBUG: Check retrieval
                print(f"🔍 Co-occurrences retrieved from database: {len(cooccurrences)}")
                for cooc in cooccurrences[:3]:
                    print(f"    {cooc.keyword1} + {cooc.keyword2}: {cooc.cooccurrence_count}")

                results['cooccurrences'] = []
                for cooc in cooccurrences:
                    results['cooccurrences'].append({
                        'keyword1': cooc.keyword1,
                        'keyword2': cooc.keyword2,
                        'cooccurrence_count': cooc.cooccurrence_count,
                        'in_posts': cooc.in_posts,
                        'in_comments': cooc.in_comments,
                        'avg_sentiment': cooc.avg_sentiment or 0.0
                    })
    
                # DEBUG: Check what we're adding to results
                print(f"🔍 Co-occurrences added to results: {len(results['cooccurrences'])}")
    
            finally:
                session.close()
        
            # Get trend summaries for ALL keywords (no limit for project summaries)
            keywords = results.get('keywords', [])
            print(f"🔍 Processing trends for {len(keywords)} keywords: {keywords}")

            if keywords:
                # Use limit_keywords=False to process ALL keywords for project summaries
                trend_data = trends_analyzer.get_trends_data(
                    session_id, keywords, 'biweekly', limit_keywords=False
                )
                print(f"🔍 Trend data keys: {trend_data.get('trends', {}).keys()}")

                trend_summary = trends_analyzer.get_trend_summary(trend_data)
                print(f"🔍 Trend summary computed for: {list(trend_summary.keys())}")

                results['trend_summaries'] = {}
                for keyword, summary_info in trend_summary.items():
                    print(f"    {keyword}: {summary_info.get('trend_direction', 'unknown')} ({summary_info.get('total_mentions', 0)} mentions)")
                    results['trend_summaries'][keyword] = {
                        'trend_direction': summary_info['trend_direction'],
                        'total_mentions': summary_info['total_mentions']
                    }

                print(f"🔍 Trend summaries added to results: {len(results['trend_summaries'])}")
        
            # Get enhanced sample contexts (5 most recent with all keyword mentions)
            if keywords:
                results['sample_contexts'] = self.get_enhanced_sample_contexts(session_id, limit=8)
    
        return results
    
    def get_session_results(self, session_id: str) -> Dict[str, Any]:
        """
        Get comprehensive results for an analysis session.
        
        Args:
            session_id: Session ID to get results for
        
        Returns:
            Dictionary with complete session results
        """
        analysis_session = db.get_analysis_session(session_id)
        if not analysis_session:
            raise ValueError(f"Analysis session not found: {session_id}")
        
        # Get keyword statistics
        session = db.get_session()
        try:
            keyword_stats = session.query(KeywordStat).filter(
                KeywordStat.analysis_session_id == session_id
            ).all()
            
            # Format keyword stats
            keywords_data = []
            for stat in keyword_stats:
                keywords_data.append({
                    'keyword': stat.keyword,
                    'total_mentions': stat.total_mentions,
                    'avg_sentiment': stat.avg_sentiment,
                    'posts_found_in': stat.posts_found_in,
                    'comments_found_in': stat.comments_found_in,
                    'collections_found_in': json.loads(stat.collections_found_in),
                    'first_mention_date': stat.first_mention_date,
                    'last_mention_date': stat.last_mention_date
                })
            
            # Sort by mentions (descending)
            keywords_data.sort(key=lambda x: x['total_mentions'], reverse=True)
            
            return {
                'session_id': session_id,
                'name': analysis_session.name,
                'status': analysis_session.status,
                'created_at': analysis_session.created_at,
                'keywords': json.loads(analysis_session.keywords),
                'collection_ids': json.loads(analysis_session.collection_ids),
                'partial_matching': analysis_session.partial_matching,
                'context_window_words': analysis_session.context_window_words,
                'total_mentions': analysis_session.total_mentions,
                'avg_sentiment': analysis_session.avg_sentiment,
                'keywords_data': keywords_data
            }
        
        finally:
            session.close()
    
    def get_keyword_details(self, session_id: str, keyword: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific keyword in a session.
        
        Args:
            session_id: Session ID
            keyword: Keyword to get details for
        
        Returns:
            Dictionary with keyword details
        """
        session = db.get_session()
        try:
            # Get keyword statistics
            keyword_stat = session.query(KeywordStat).filter(
                KeywordStat.analysis_session_id == session_id,
                KeywordStat.keyword == keyword
            ).first()
            
            if not keyword_stat:
                raise ValueError(f"Keyword '{keyword}' not found in session {session_id}")
            
            # Get recent mentions (last 10)
            recent_mentions = session.query(KeywordMention).filter(
                KeywordMention.analysis_session_id == session_id,
                KeywordMention.keyword == keyword
            ).order_by(KeywordMention.created_utc.desc()).limit(10).all()
            
            mentions_data = []
            for mention in recent_mentions:
                mentions_data.append({
                    'content_type': mention.content_type,
                    'content_reddit_id': mention.content_reddit_id,
                    'sentiment_score': mention.sentiment_score,
                    'created_utc': mention.created_utc,
                    'position_in_content': mention.position_in_content
                })
            
            return {
                'keyword': keyword,
                'total_mentions': keyword_stat.total_mentions,
                'avg_sentiment': keyword_stat.avg_sentiment,
                'posts_found_in': keyword_stat.posts_found_in,
                'comments_found_in': keyword_stat.comments_found_in,
                'collections_found_in': json.loads(keyword_stat.collections_found_in),
                'first_mention_date': keyword_stat.first_mention_date,
                'last_mention_date': keyword_stat.last_mention_date,
                'recent_mentions': mentions_data
            }
        
        finally:
            session.close()
    
    def get_trends(self, session_id: str, keywords: List[str], time_period: str = 'weekly') -> Dict[str, Any]:
        """
        Get trend analysis for specified keywords.
        
        Args:
            session_id: Session ID
            keywords: List of keywords to analyze (max 5)
            time_period: 'daily', 'weekly', or 'monthly'
        
        Returns:
            Dictionary with trends data
        """
        return trends_analyzer.get_trends_data(session_id, keywords, time_period)
    
    def get_relationships(self, session_id: str, keyword: str) -> Dict[str, Any]:
        """
        Get co-occurrence relationships for a keyword.
        
        Args:
            session_id: Session ID
            keyword: Keyword to get relationships for
        
        Returns:
            Dictionary with relationship data
        """
        session = db.get_session()
        try:
            # Get all co-occurrences for this keyword
            cooccurrences = session.query(KeywordCooccurrence).filter(
                KeywordCooccurrence.analysis_session_id == session_id
            ).filter(
                (KeywordCooccurrence.keyword1 == keyword) | 
                (KeywordCooccurrence.keyword2 == keyword)
            ).order_by(KeywordCooccurrence.cooccurrence_count.desc()).all()
            
            relationships = []
            for cooc in cooccurrences:
                related_keyword = cooc.keyword2 if cooc.keyword1 == keyword else cooc.keyword1
                relationships.append({
                    'keyword': related_keyword,
                    'cooccurrence_count': cooc.cooccurrence_count,
                    'in_posts': cooc.in_posts,
                    'in_comments': cooc.in_comments
                })
            
            return {
                'target_keyword': keyword,
                'relationships': relationships
            }
        
        finally:
            session.close()
    
    def get_context_instances(self, session_id: str, keyword: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get context instances where a keyword appears.
    
        Args:
            session_id: Session ID
            keyword: Keyword to get contexts for
            limit: Maximum number of instances to return
    
        Returns:
            Dictionary with context instances
        """
        session = db.get_session()
        try:
            # Get keyword mentions
            mentions = session.query(KeywordMention).filter(
                KeywordMention.analysis_session_id == session_id,
                KeywordMention.keyword == keyword
            ).order_by(KeywordMention.created_utc.desc()).limit(limit).all()
        
            # Get actual content for each mention
            contexts = []
            for mention in mentions:
                # Get the actual post/comment content
                if mention.content_type == 'post':
                    content_obj = session.query(Post).filter(
                        Post.reddit_id == mention.content_reddit_id,
                        Post.collection_id == mention.collection_id
                    ).first()
                
                    if content_obj:
                        full_text = content_obj.title
                        if content_obj.content:
                            full_text += ' ' + content_obj.content
                else:  # comment
                    content_obj = session.query(Comment).filter(
                        Comment.reddit_id == mention.content_reddit_id,
                        Comment.collection_id == mention.collection_id
                    ).first()
                
                    if content_obj:
                        full_text = content_obj.content
            
                if content_obj and full_text:
                    # Extract context around the keyword
                    context = sentiment_analyzer.extract_context_window(
                        full_text, keyword, mention.position_in_content, 30  # Larger window for context view
                    )
                
                    contexts.append({
                        'content_type': mention.content_type,
                        'content_reddit_id': mention.content_reddit_id,
                        'context': context,
                        'sentiment_score': mention.sentiment_score,
                        'created_utc': mention.created_utc,
                        'collection_id': mention.collection_id
                    })
        
            return {
                'keyword': keyword,
                'total_contexts': len(contexts),
                'contexts': contexts
            }
    
        finally:
            session.close()

    def get_enhanced_sample_contexts(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get sample contexts with all keyword mentions for preview display.
    
        Args:
            session_id: Session ID
            limit: Maximum number of contexts to return
    
        Returns:
            List of enhanced context instances with all keyword mentions
        """
        session = db.get_session()
        try:
            # Get all keyword mentions ordered by recency
            all_mentions = session.query(KeywordMention).filter(
                KeywordMention.analysis_session_id == session_id
            ).order_by(KeywordMention.created_utc.desc()).all()
        
            # Group mentions by content (same reddit_id + collection_id)
            content_groups = defaultdict(list)
            for mention in all_mentions:
                content_key = (mention.content_reddit_id, mention.collection_id, mention.content_type)
                content_groups[content_key].append(mention)
        
            # Get the most recent content pieces
            recent_content_keys = list(content_groups.keys())[:limit * 2]  # Get extra to ensure we have enough after filtering
        
            enhanced_contexts = []
            for content_key in recent_content_keys:
                if len(enhanced_contexts) >= limit:
                    break
                
                content_reddit_id, collection_id, content_type = content_key
                mentions_for_content = content_groups[content_key]
            
                # Get the actual content
                if content_type == 'post':
                    content_obj = session.query(Post).filter(
                        Post.reddit_id == content_reddit_id,
                        Post.collection_id == collection_id
                    ).first()
                
                    if content_obj:
                        full_text = content_obj.title
                        if content_obj.content:
                            full_text += ' ' + content_obj.content
                else:  # comment
                    content_obj = session.query(Comment).filter(
                        Comment.reddit_id == content_reddit_id,
                        Comment.collection_id == collection_id
                    ).first()
                
                    if content_obj:
                        full_text = content_obj.content
            
                if content_obj and full_text:
                    # Create enhanced context with all keyword mentions
                    keyword_mentions = []
                    sentiment_scores = []
                
                    for mention in mentions_for_content:
                        keyword_mentions.append({
                            'keyword': mention.keyword,
                            'position_in_content': mention.position_in_content,
                            'sentiment_score': mention.sentiment_score
                        })
                        sentiment_scores.append(mention.sentiment_score)
                
                    # Calculate average sentiment
                    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
                
                    # Use the most recent mention for timestamp
                    most_recent_mention = max(mentions_for_content, key=lambda m: m.created_utc)
                
                    enhanced_contexts.append({
                        'content_type': content_type,
                        'content_reddit_id': content_reddit_id,
                        'collection_id': collection_id,
                        'context': full_text,  # We'll handle windowing in the frontend
                        'sentiment_score': avg_sentiment,
                        'created_utc': most_recent_mention.created_utc,
                        'keyword_mentions': keyword_mentions
                    })
        
            return enhanced_contexts
    
        finally:
            session.close()
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete an analysis session and all related data.
        
        Args:
            session_id: Session ID to delete
        
        Returns:
            True if deleted successfully, False if session not found
        """
        return db.delete_analysis_session(session_id)
    
    # Helper methods
    
    def _get_collection_content(self, collection_id: str) -> tuple:
        """Get posts and comments for a collection."""
        session = db.get_session()
        try:
            posts = session.query(Post).filter(Post.collection_id == collection_id).all()
            comments = session.query(Comment).filter(Comment.collection_id == collection_id).all()
            
            # Convert to dictionaries
            posts_data = []
            for post in posts:
                posts_data.append({
                    'reddit_id': post.reddit_id,
                    'collection_id': post.collection_id,
                    'title': post.title,
                    'content': post.content or '',
                    'created_utc': post.created_utc
                })
            
            comments_data = []
            for comment in comments:
                comments_data.append({
                    'reddit_id': comment.reddit_id,
                    'collection_id': comment.collection_id,
                    'content': comment.content,
                    'created_utc': comment.created_utc
                })
            
            return posts_data, comments_data
        
        finally:
            session.close()
    
    def _save_keyword_mentions_batch(self, mentions: List[Dict[str, Any]]):
        """Save keyword mentions in batches."""
        if not mentions:
            return
        
        session = db.get_session()
        try:
            batch_size = 100
            
            with tqdm(total=len(mentions), desc="Saving mentions", unit="mention") as pbar:
                for i in range(0, len(mentions), batch_size):
                    batch = mentions[i:i + batch_size]
                    
                    for mention_data in batch:
                        mention = KeywordMention(**mention_data)
                        session.add(mention)
                    
                    session.commit()
                    pbar.update(len(batch))
        
        finally:
            session.close()
    
    def _calculate_keyword_stats(self, session_id: str, keywords: List[str]) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics for each keyword."""
        session = db.get_session()
        try:
            stats = {}
            
            for keyword in keywords:
                mentions = session.query(KeywordMention).filter(
                    KeywordMention.analysis_session_id == session_id,
                    KeywordMention.keyword == keyword
                ).all()
                
                if not mentions:
                    continue
                
                # Calculate statistics
                total_mentions = len(mentions)
                avg_sentiment = sum(m.sentiment_score for m in mentions) / total_mentions
                posts_found_in = len(set(m.content_reddit_id for m in mentions if m.content_type == 'post'))
                comments_found_in = len(set(m.content_reddit_id for m in mentions if m.content_type == 'comment'))
                collections_found_in = list(set(m.collection_id for m in mentions))
                first_mention_date = min(m.created_utc for m in mentions)
                last_mention_date = max(m.created_utc for m in mentions)
                
                stats[keyword] = {
                    'total_mentions': total_mentions,
                    'avg_sentiment': avg_sentiment,
                    'posts_found_in': posts_found_in,
                    'comments_found_in': comments_found_in,
                    'collections_found_in': collections_found_in,
                    'first_mention_date': first_mention_date,
                    'last_mention_date': last_mention_date
                }
            
            return stats
        
        finally:
            session.close()
    
    def _save_keyword_stats_batch(self, session_id: str, stats: Dict[str, Dict[str, Any]]):
        """Save keyword statistics in batch."""
        if not stats:
            return
        
        session = db.get_session()
        try:
            for keyword, stat_data in stats.items():
                keyword_stat = KeywordStat(
                    analysis_session_id=session_id,
                    keyword=keyword,
                    total_mentions=stat_data['total_mentions'],
                    avg_sentiment=stat_data['avg_sentiment'],
                    posts_found_in=stat_data['posts_found_in'],
                    comments_found_in=stat_data['comments_found_in'],
                    collections_found_in=json.dumps(stat_data['collections_found_in']),
                    first_mention_date=stat_data['first_mention_date'],
                    last_mention_date=stat_data['last_mention_date']
                )
                session.add(keyword_stat)
            
            session.commit()
        
        finally:
            session.close()
    
    def _save_cooccurrences_batch(self, session_id: str, cooccurrence_data: Dict[str, Any]):
        """Save co-occurrence data in batch."""
        if not cooccurrence_data.get('pairs'):
            return
        
        session = db.get_session()
        try:
            for (keyword1, keyword2), stats in cooccurrence_data['pairs'].items():
                cooccurrence = KeywordCooccurrence(
                    analysis_session_id=session_id,
                    keyword1=keyword1,
                    keyword2=keyword2,
                    cooccurrence_count=stats['total_count'],
                    in_posts=stats['in_posts'],
                    in_comments=stats['in_comments'],
                    avg_sentiment=stats['avg_sentiment']
                )
                session.add(cooccurrence)
            
            session.commit()
        
        finally:
            session.close()
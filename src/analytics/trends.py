"""
Trends Analysis Module

Handles on-demand computation of keyword mention and sentiment trends
over time with configurable time groupings.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
from ..database import db, KeywordMention
import json


class TrendsAnalyzer:
    def __init__(self):
        pass
    
    def get_trends_data(self, session_id: str, keywords: List[str], 
                       time_period: str = 'daily') -> Dict[str, Any]:
        """
        Get trends data for specified keywords from an analysis session.
        
        Args:
            session_id: Analysis session ID
            keywords: List of keywords to analyze (max 5 recommended)
            time_period: 'daily', 'weekly', or 'monthly'
        
        Returns:
            Dictionary with trends data for each keyword
        """
        if not keywords:
            return {'trends': {}, 'time_period': time_period}
        
        # Limit to 5 keywords for performance
        keywords = keywords[:5]
        
        session = db.get_session()
        try:
            # Query keyword mentions for the specified keywords
            mentions = session.query(KeywordMention).filter(
                KeywordMention.analysis_session_id == session_id,
                KeywordMention.keyword.in_(keywords)
            ).order_by(KeywordMention.created_utc).all()
            
            # Group data by time period and keyword
            trends_data = self._group_mentions_by_time(mentions, time_period)
            
            return {
                'trends': trends_data,
                'time_period': time_period,
                'keywords_analyzed': keywords
            }
        
        finally:
            session.close()
    
    def _group_mentions_by_time(self, mentions: List[KeywordMention], 
                               time_period: str) -> Dict[str, Dict[str, Any]]:
        """
        Group keyword mentions by time period.
        
        Args:
            mentions: List of KeywordMention objects
            time_period: 'daily', 'weekly', or 'monthly'
        
        Returns:
            Dictionary grouped by keyword and time period
        """
        trends = defaultdict(lambda: defaultdict(lambda: {
            'mentions': 0,
            'sentiment_scores': [],
            'avg_sentiment': 0.0
        }))
        
        for mention in mentions:
            # Convert timestamp to date
            mention_date = datetime.fromtimestamp(mention.created_utc).date()
            
            # Group by time period
            time_key = self._get_time_key(mention_date, time_period)
            
            # Update statistics
            trends[mention.keyword][time_key]['mentions'] += 1
            trends[mention.keyword][time_key]['sentiment_scores'].append(mention.sentiment_score)
        
        # Calculate average sentiment for each time period
        for keyword in trends:
            for time_key in trends[keyword]:
                sentiment_scores = trends[keyword][time_key]['sentiment_scores']
                if sentiment_scores:
                    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                    trends[keyword][time_key]['avg_sentiment'] = round(avg_sentiment, 4)
                
                # Remove raw sentiment scores to reduce data size
                del trends[keyword][time_key]['sentiment_scores']
        
        # Convert to regular dict for JSON serialization
        return {keyword: dict(time_data) for keyword, time_data in trends.items()}
    
    def _get_time_key(self, mention_date: date, time_period: str) -> str:
        """
        Generate time key for grouping based on time period.
        
        Args:
            mention_date: Date of the mention
            time_period: 'daily', 'weekly', or 'monthly'
        
        Returns:
            String key for time grouping
        """
        if time_period == 'daily':
            return mention_date.strftime('%Y-%m-%d')
        elif time_period == 'weekly':
            # Get Monday of the week
            days_since_monday = mention_date.weekday()
            monday = mention_date - timedelta(days=days_since_monday)
            return monday.strftime('%Y-%m-%d')  # Monday of the week
        elif time_period == 'monthly':
            return mention_date.strftime('%Y-%m')
        else:
            raise ValueError(f"Invalid time period: {time_period}")
    
    def get_trend_summary(self, trends_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Generate summary statistics for trends data.
        
        Args:
            trends_data: Output from get_trends_data
        
        Returns:
            Summary statistics for each keyword
        """
        summary = {}
        
        for keyword, time_data in trends_data['trends'].items():
            if not time_data:
                continue
            
            # Calculate total mentions and average sentiment
            total_mentions = sum(period['mentions'] for period in time_data.values())
            avg_sentiment = sum(period['avg_sentiment'] * period['mentions'] 
                              for period in time_data.values()) / total_mentions if total_mentions > 0 else 0
            
            # Calculate trend direction (comparing first and last periods)
            time_keys = sorted(time_data.keys())
            if len(time_keys) >= 2:
                first_period_mentions = time_data[time_keys[0]]['mentions']
                last_period_mentions = time_data[time_keys[-1]]['mentions']
                
                if last_period_mentions > first_period_mentions:
                    trend_direction = 'rising'
                elif last_period_mentions < first_period_mentions:
                    trend_direction = 'falling'
                else:
                    trend_direction = 'stable'
            else:
                trend_direction = 'insufficient_data'
            
            summary[keyword] = {
                'total_mentions': total_mentions,
                'avg_sentiment': round(avg_sentiment, 4),
                'trend_direction': trend_direction,
                'time_periods': len(time_keys),
                'first_period': time_keys[0] if time_keys else None,
                'last_period': time_keys[-1] if time_keys else None
            }
        
        return summary
    
    def format_trends_for_display(self, trends_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format trends data for display in CLI or frontend.
        
        Args:
            trends_data: Output from get_trends_data
        
        Returns:
            List of formatted trend entries for display
        """
        formatted_trends = []
        
        # Get all unique time periods across all keywords
        all_time_periods = set()
        for keyword_data in trends_data['trends'].values():
            all_time_periods.update(keyword_data.keys())
        
        sorted_periods = sorted(list(all_time_periods))
        
        # Format data for each time period
        for period in sorted_periods:
            period_data = {
                'time_period': period,
                'keywords': {}
            }
            
            for keyword, keyword_data in trends_data['trends'].items():
                if period in keyword_data:
                    period_data['keywords'][keyword] = {
                        'mentions': keyword_data[period]['mentions'],
                        'avg_sentiment': keyword_data[period]['avg_sentiment']
                    }
                else:
                    period_data['keywords'][keyword] = {
                        'mentions': 0,
                        'avg_sentiment': 0.0
                    }
            
            formatted_trends.append(period_data)
        
        return formatted_trends


# Global trends analyzer instance
trends_analyzer = TrendsAnalyzer()
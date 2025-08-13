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
                   time_period: str = 'weekly', limit_keywords: bool = True) -> Dict[str, Any]:
        """
        Get trends data for specified keywords from an analysis session.
        
        Args:
            session_id: Analysis session ID
            keywords: List of keywords to analyze
            time_period: 'daily', 'weekly', or 'monthly'
            limit_keywords: If True, limit to 5 keywords for performance (default: True)
                        If False, process all keywords (used for project summaries)
        
        Returns:
            Dictionary with trends data for each keyword
        """
        if not keywords:
            return {'trends': {}, 'time_period': time_period}
        
        # Only limit keywords when explicitly requested (for interactive features)
        if limit_keywords:
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
            time_period: 'daily', 'weekly', 'biweekly', or 'monthly'
        
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
        elif time_period == 'biweekly':
            # Get 2-week periods using a universal reference point
            # Using Unix epoch start (1970-01-05) which was a Monday
            from datetime import date as date_class
            epoch_monday = date_class(1970, 1, 5)  # Monday, January 5, 1970
            
            days_diff = (mention_date - epoch_monday).days
            biweek_number = days_diff // 14  # 14 days = 2 weeks
            
            # Calculate the start of this 2-week period
            biweek_start = epoch_monday + timedelta(days=biweek_number * 14)
            return biweek_start.strftime('%Y-%m-%d')  # Start date of the 2-week period
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
    
    def format_trends_for_charts(self, trends_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format trends data specifically for chart visualization (Recharts).
        
        Args:
            trends_data: Output from get_trends_data
        
        Returns:
            Chart-optimized data structure with flat arrays and complete time series
        """
        if not trends_data.get('trends'):
            return {
                'keywords_analyzed': [],
                'time_period': trends_data.get('time_period', 'weekly'),
                'date_range': {'start_date': None, 'end_date': None},
                'chart_data': [],
                'summary': {'total_periods': 0, 'total_mentions': 0, 'date_coverage': 'No data'}
            }
        
        keywords = trends_data.get('keywords_analyzed', [])
        time_period = trends_data.get('time_period', 'weekly')
        
        # Get all unique time periods and sort them
        all_time_periods = set()
        for keyword_data in trends_data['trends'].values():
            all_time_periods.update(keyword_data.keys())
        
        sorted_periods = sorted(list(all_time_periods))
        
        if not sorted_periods:
            return {
                'keywords_analyzed': keywords,
                'time_period': time_period,
                'date_range': {'start_date': None, 'end_date': None},
                'chart_data': [],
                'summary': {'total_periods': 0, 'total_mentions': 0, 'date_coverage': 'No data'}
            }
        
        # Build chart data array with flat structure
        chart_data = []
        total_mentions = 0
        
        for period in sorted_periods:
            data_point = {
                'time_period': period,
                'formatted_date': self._format_date_for_display(period, time_period)
            }
            
            # Add data for each keyword
            for keyword in keywords:
                keyword_data = trends_data['trends'].get(keyword, {})
                period_data = keyword_data.get(period, {'mentions': 0, 'avg_sentiment': 0.0})
                
                # Use safe field names for Recharts (replace special characters)
                safe_keyword = keyword.replace('-', '_').replace(' ', '_').replace('.', '_')
                data_point[f'{safe_keyword}_mentions'] = period_data['mentions']
                data_point[f'{safe_keyword}_sentiment'] = period_data['avg_sentiment']
                
                total_mentions += period_data['mentions']
            
            chart_data.append(data_point)
        
        # Calculate date range and coverage
        start_date = sorted_periods[0]
        end_date = sorted_periods[-1]
        date_coverage = self._calculate_date_coverage(len(sorted_periods), time_period)
        
        return {
            'keywords_analyzed': keywords,
            'time_period': time_period,
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'chart_data': chart_data,
            'summary': {
                'total_periods': len(sorted_periods),
                'total_mentions': total_mentions,
                'date_coverage': date_coverage
            }
        }
    
    def _format_date_for_display(self, time_key: str, time_period: str) -> str:
        """
        Format time key for human-readable display in charts.
        
        Args:
            time_key: Time period key (e.g., '2024-01-15' or '2024-01')
            time_period: Period type ('daily', 'weekly', 'monthly')
        
        Returns:
            Human-readable date string
        """
        try:
            if time_period == 'daily':
                date_obj = datetime.strptime(time_key, '%Y-%m-%d').date()
                return date_obj.strftime('%b %d, %Y')  # "Jan 15, 2024"
            elif time_period == 'weekly':
                # time_key is Monday of the week
                date_obj = datetime.strptime(time_key, '%Y-%m-%d').date()
                return f"Week of {date_obj.strftime('%b %d, %Y')}"  # "Week of Jan 15, 2024"
            elif time_period == 'monthly':
                date_obj = datetime.strptime(time_key, '%Y-%m').date()
                return date_obj.strftime('%B %Y')  # "January 2024"
            else:
                return time_key
        except ValueError:
            return time_key
    
    def _calculate_date_coverage(self, period_count: int, time_period: str) -> str:
        """
        Calculate human-readable date coverage description.
        
        Args:
            period_count: Number of time periods
            time_period: Period type ('daily', 'weekly', 'monthly')
        
        Returns:
            Human-readable coverage string
        """
        if period_count == 0:
            return 'No data'
        elif period_count == 1:
            return f'1 {time_period[:-2]}'  # Remove 'ly' from 'daily'/'weekly'/'monthly'
        else:
            period_name = time_period[:-2] if time_period.endswith('ly') else time_period
            if period_name == 'dai':
                period_name = 'day'
            elif period_name == 'week':
                period_name = 'week'
            elif period_name == 'month':
                period_name = 'month'
            
            return f'{period_count} {period_name}s'
        
    


# Global trends analyzer instance
trends_analyzer = TrendsAnalyzer()
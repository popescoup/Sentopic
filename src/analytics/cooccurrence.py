"""
Co-occurrence Detection Module

Handles detection and counting of keyword co-occurrences within
the same posts or comments.
"""

from typing import List, Dict, Any, Set, Tuple, Optional
from collections import defaultdict
from .keywords import keyword_processor


class CooccurrenceDetector:
    def __init__(self):
        pass
    
    def find_cooccurrences_in_content(self, content_data: Dict[str, Any], keywords: List[str],
                                     partial_matching: bool = False) -> List[Tuple[str, str]]:
        """
        Find all keyword co-occurrences in a single piece of content.
        
        Args:
            content_data: Dictionary with content data (post or comment)
            keywords: List of keywords to search for
            partial_matching: If True, use partial matching
        
        Returns:
            List of keyword pairs (tuples) that co-occur in the content
        """
        # Get unique keywords found in this content
        found_keywords = keyword_processor.get_unique_keywords_in_content(
            content_data, keywords, partial_matching
        )
        
        # Convert to sorted list for consistent pair generation
        found_keywords_list = sorted(list(found_keywords))
        
        # Generate all possible pairs
        pairs = []
        for i in range(len(found_keywords_list)):
            for j in range(i + 1, len(found_keywords_list)):
                keyword1 = found_keywords_list[i]
                keyword2 = found_keywords_list[j]
                # Store in alphabetical order for consistency
                if keyword1 < keyword2:
                    pairs.append((keyword1, keyword2))
                else:
                    pairs.append((keyword2, keyword1))
        
        return pairs
    
    def process_content_for_cooccurrences(self, posts: List[Dict[str, Any]], 
                                         comments: List[Dict[str, Any]], 
                                         keywords: List[str],
                                         partial_matching: bool = False,
                                         keyword_mentions: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process all posts and comments to find keyword co-occurrences with sentiment analysis.
        
        Args:
            posts: List of post dictionaries
            comments: List of comment dictionaries
            keywords: List of keywords to search for
            partial_matching: If True, use partial matching
            keyword_mentions: Optional list of keyword mentions with sentiment data
        
        Returns:
            Dictionary with co-occurrence statistics including sentiment:
            {
                'pairs': {
                    ('keyword1', 'keyword2'): {
                        'total_count': int,
                        'in_posts': int,
                        'in_comments': int,
                        'avg_sentiment': float
                    }
                }
            }
        """
        cooccurrence_stats = defaultdict(lambda: {
            'total_count': 0,
            'in_posts': 0,
            'in_comments': 0,
            'sentiment_values': []  # Collect sentiment values for averaging
        })
        
        # Create a lookup map for sentiment data if provided
        sentiment_lookup = {}
        if keyword_mentions:
            for mention in keyword_mentions:
                content_key = (mention['content_reddit_id'], mention['collection_id'], mention['content_type'])
                if content_key not in sentiment_lookup:
                    sentiment_lookup[content_key] = []
                sentiment_lookup[content_key].append({
                    'keyword': mention['keyword'],
                    'sentiment_score': mention['sentiment_score']
                })
        
        # Process posts
        for post in posts:
            pairs = self.find_cooccurrences_in_content(post, keywords, partial_matching)
            for pair in pairs:
                cooccurrence_stats[pair]['total_count'] += 1
                cooccurrence_stats[pair]['in_posts'] += 1
                
                # Calculate sentiment for this content piece if data available
                if keyword_mentions:
                    content_key = (post['reddit_id'], post['collection_id'], 'post')
                    content_sentiment = self._calculate_content_pair_sentiment(
                        content_key, pair, sentiment_lookup
                    )
                    if content_sentiment is not None:
                        cooccurrence_stats[pair]['sentiment_values'].append(content_sentiment)
        
        # Process comments
        for comment in comments:
            pairs = self.find_cooccurrences_in_content(comment, keywords, partial_matching)
            for pair in pairs:
                cooccurrence_stats[pair]['total_count'] += 1
                cooccurrence_stats[pair]['in_comments'] += 1
                
                # Calculate sentiment for this content piece if data available
                if keyword_mentions:
                    content_key = (comment['reddit_id'], comment['collection_id'], 'comment')
                    content_sentiment = self._calculate_content_pair_sentiment(
                        content_key, pair, sentiment_lookup
                    )
                    if content_sentiment is not None:
                        cooccurrence_stats[pair]['sentiment_values'].append(content_sentiment)
        
        # Calculate final average sentiment for each pair
        final_stats = {}
        for pair, stats in cooccurrence_stats.items():
            final_stats[pair] = {
                'total_count': stats['total_count'],
                'in_posts': stats['in_posts'],
                'in_comments': stats['in_comments'],
                'avg_sentiment': sum(stats['sentiment_values']) / len(stats['sentiment_values']) 
                               if stats['sentiment_values'] else 0.0
            }
        
        return {'pairs': final_stats}
    
    def get_cooccurrences_for_keyword(self, cooccurrence_data: Dict[str, Any], 
                                     target_keyword: str) -> List[Dict[str, Any]]:
        """
        Get all co-occurrences for a specific keyword.
        
        Args:
            cooccurrence_data: Co-occurrence data from process_content_for_cooccurrences
            target_keyword: The keyword to find co-occurrences for
        
        Returns:
            List of co-occurrence dictionaries sorted by count (descending)
        """
        relationships = []
        
        for (keyword1, keyword2), stats in cooccurrence_data['pairs'].items():
            if keyword1 == target_keyword:
                relationships.append({
                    'keyword': keyword2,
                    'cooccurrence_count': stats['total_count'],
                    'in_posts': stats['in_posts'],
                    'in_comments': stats['in_comments']
                })
            elif keyword2 == target_keyword:
                relationships.append({
                    'keyword': keyword1,
                    'cooccurrence_count': stats['total_count'],
                    'in_posts': stats['in_posts'],
                    'in_comments': stats['in_comments']
                })
        
        # Sort by co-occurrence count (descending)
        relationships.sort(key=lambda x: x['cooccurrence_count'], reverse=True)
        
        return relationships
    
    def get_top_cooccurrences(self, cooccurrence_data: Dict[str, Any], 
                             limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the top co-occurring keyword pairs.
        
        Args:
            cooccurrence_data: Co-occurrence data from process_content_for_cooccurrences
            limit: Maximum number of pairs to return
        
        Returns:
            List of top co-occurrence dictionaries sorted by count (descending)
        """
        pairs_list = []
        
        for (keyword1, keyword2), stats in cooccurrence_data['pairs'].items():
            pairs_list.append({
                'keyword1': keyword1,
                'keyword2': keyword2,
                'cooccurrence_count': stats['total_count'],
                'in_posts': stats['in_posts'],
                'in_comments': stats['in_comments']
            })
        
        # Sort by co-occurrence count (descending)
        pairs_list.sort(key=lambda x: x['cooccurrence_count'], reverse=True)
        
        return pairs_list[:limit]
    
    def _calculate_content_pair_sentiment(self, content_key: Tuple[str, str, str], 
                                         keyword_pair: Tuple[str, str], 
                                         sentiment_lookup: Dict) -> Optional[float]:
        """
        Calculate average sentiment for a keyword pair within a single content piece.
        
        Args:
            content_key: (content_reddit_id, collection_id, content_type)
            keyword_pair: (keyword1, keyword2) tuple
            sentiment_lookup: Dictionary mapping content_key to list of keyword mentions with sentiment
        
        Returns:
            Average sentiment for this keyword pair in this content piece, or None if no data
        """
        if content_key not in sentiment_lookup:
            return None
        
        keyword1, keyword2 = keyword_pair
        content_mentions = sentiment_lookup[content_key]
        
        # Get all sentiment values for both keywords in this content
        relevant_sentiments = []
        for mention in content_mentions:
            if mention['keyword'] in (keyword1, keyword2):
                relevant_sentiments.append(mention['sentiment_score'])
        
        if not relevant_sentiments:
            return None
        
        return sum(relevant_sentiments) / len(relevant_sentiments)


# Global co-occurrence detector instance
cooccurrence_detector = CooccurrenceDetector()
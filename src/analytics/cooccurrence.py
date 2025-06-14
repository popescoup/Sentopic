"""
Co-occurrence Detection Module

Handles detection and counting of keyword co-occurrences within
the same posts or comments.
"""

from typing import List, Dict, Any, Set, Tuple
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
                                         partial_matching: bool = False) -> Dict[str, Any]:
        """
        Process all posts and comments to find keyword co-occurrences.
        
        Args:
            posts: List of post dictionaries
            comments: List of comment dictionaries
            keywords: List of keywords to search for
            partial_matching: If True, use partial matching
        
        Returns:
            Dictionary with co-occurrence statistics:
            {
                'pairs': {
                    ('keyword1', 'keyword2'): {
                        'total_count': int,
                        'in_posts': int,
                        'in_comments': int
                    }
                }
            }
        """
        cooccurrence_stats = defaultdict(lambda: {
            'total_count': 0,
            'in_posts': 0,
            'in_comments': 0
        })
        
        # Process posts
        for post in posts:
            pairs = self.find_cooccurrences_in_content(post, keywords, partial_matching)
            for pair in pairs:
                cooccurrence_stats[pair]['total_count'] += 1
                cooccurrence_stats[pair]['in_posts'] += 1
        
        # Process comments
        for comment in comments:
            pairs = self.find_cooccurrences_in_content(comment, keywords, partial_matching)
            for pair in pairs:
                cooccurrence_stats[pair]['total_count'] += 1
                cooccurrence_stats[pair]['in_comments'] += 1
        
        return {'pairs': dict(cooccurrence_stats)}
    
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


# Global co-occurrence detector instance
cooccurrence_detector = CooccurrenceDetector()
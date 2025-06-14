"""
Keyword Processing Module

Handles keyword search, matching (exact/partial), and position tracking
in Reddit posts and comments.
"""

import re
from typing import List, Dict, Any, Tuple, Set


class KeywordProcessor:
    def __init__(self):
        pass
    
    def find_keywords_in_text(self, text: str, keywords: List[str], 
                             partial_matching: bool = False) -> List[Dict[str, Any]]:
        """
        Find all keyword occurrences in text with their positions.
        
        Args:
            text: Text to search in
            keywords: List of keywords to search for
            partial_matching: If True, use partial matching; if False, exact matching
        
        Returns:
            List of dictionaries with keyword occurrence data:
            [{'keyword': str, 'position': int, 'matched_text': str}, ...]
        """
        if not text or not keywords:
            return []
        
        matches = []
        text_lower = text.lower()
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            if partial_matching:
                # Partial matching: keyword can be part of a larger word
                pattern = re.escape(keyword_lower)
                for match in re.finditer(pattern, text_lower):
                    matches.append({
                        'keyword': keyword,
                        'position': match.start(),
                        'matched_text': text[match.start():match.end()]
                    })
            else:
                # Exact matching: keyword must be a complete word
                pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                for match in re.finditer(pattern, text_lower):
                    matches.append({
                        'keyword': keyword,
                        'position': match.start(),
                        'matched_text': text[match.start():match.end()]
                    })
        
        # Sort by position for consistent ordering
        matches.sort(key=lambda x: x['position'])
        return matches
    
    def find_keywords_in_content(self, content_data: Dict[str, Any], keywords: List[str],
                                partial_matching: bool = False) -> List[Dict[str, Any]]:
        """
        Find keywords in post or comment content.
        
        Args:
            content_data: Dictionary with content data (post or comment)
            keywords: List of keywords to search for
            partial_matching: If True, use partial matching
        
        Returns:
            List of keyword matches with additional metadata
        """
        # Determine content type and extract searchable text
        if 'title' in content_data:
            # This is a post - search in title and content
            content_type = 'post'
            searchable_text = content_data['title']
            if content_data.get('content'):
                searchable_text += ' ' + content_data['content']
        else:
            # This is a comment - search in content only
            content_type = 'comment'
            searchable_text = content_data.get('content', '')
        
        # Find all keyword matches
        matches = self.find_keywords_in_text(searchable_text, keywords, partial_matching)
        
        # Add metadata to each match
        for match in matches:
            match.update({
                'content_type': content_type,
                'content_reddit_id': content_data['reddit_id'],
                'collection_id': content_data['collection_id'],
                'created_utc': content_data['created_utc'],
                'full_text': searchable_text
            })
        
        return matches
    
    def get_unique_keywords_in_content(self, content_data: Dict[str, Any], keywords: List[str],
                                      partial_matching: bool = False) -> Set[str]:
        """
        Get unique keywords found in a piece of content (for co-occurrence analysis).
        
        Args:
            content_data: Dictionary with content data (post or comment)
            keywords: List of keywords to search for
            partial_matching: If True, use partial matching
        
        Returns:
            Set of unique keywords found in the content
        """
        matches = self.find_keywords_in_content(content_data, keywords, partial_matching)
        return set(match['keyword'] for match in matches)
    
    def process_posts_for_keywords(self, posts: List[Dict[str, Any]], keywords: List[str],
                                  partial_matching: bool = False) -> List[Dict[str, Any]]:
        """
        Process multiple posts for keyword matches.
        
        Args:
            posts: List of post dictionaries
            keywords: List of keywords to search for
            partial_matching: If True, use partial matching
        
        Returns:
            List of all keyword matches found across all posts
        """
        all_matches = []
        
        for post in posts:
            matches = self.find_keywords_in_content(post, keywords, partial_matching)
            all_matches.extend(matches)
        
        return all_matches
    
    def process_comments_for_keywords(self, comments: List[Dict[str, Any]], keywords: List[str],
                                     partial_matching: bool = False) -> List[Dict[str, Any]]:
        """
        Process multiple comments for keyword matches.
        
        Args:
            comments: List of comment dictionaries
            keywords: List of keywords to search for
            partial_matching: If True, use partial matching
        
        Returns:
            List of all keyword matches found across all comments
        """
        all_matches = []
        
        for comment in comments:
            matches = self.find_keywords_in_content(comment, keywords, partial_matching)
            all_matches.extend(matches)
        
        return all_matches


# Global keyword processor instance
keyword_processor = KeywordProcessor()
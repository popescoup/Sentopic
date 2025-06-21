"""
Content Formatter Service

Specialized formatting of Reddit content to preserve conversational structure
and natural discussion flow for optimal LLM consumption.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class ContentFormatter:
    """
    Formats Reddit posts and comments into natural conversational structures
    that preserve the essence of Reddit discussions for LLM processing.
    """
    
    def __init__(self):
        pass
    
    def format_discussion_thread(self, discussion_data: Dict[str, Any]) -> str:
        """
        Format a complete discussion thread (post + comments) into natural conversation format.
        
        Args:
            discussion_data: Dictionary with 'post' and 'comments' keys
        
        Returns:
            Formatted discussion string
        """
        formatted_parts = []
        
        # Format the main post
        if discussion_data.get('post'):
            post_section = self.format_post(discussion_data['post'])
            formatted_parts.append(post_section)
        
        # Format comments in threaded order
        if discussion_data.get('comments'):
            comments_section = self.format_comment_thread(discussion_data['comments'])
            if comments_section.strip():
                formatted_parts.append("\n" + comments_section)
        
        return "\n\n".join(formatted_parts)
    
    def format_post(self, post_data: Dict[str, Any]) -> str:
        """
        Format a Reddit post with full context and metadata.
        
        Args:
            post_data: Post data dictionary
        
        Returns:
            Formatted post string
        """
        # Extract key information
        title = post_data.get('title', 'No title')
        content = post_data.get('content', '')
        author = post_data.get('author', 'Unknown')
        score = post_data.get('score', 0)
        created_date = self._format_date(post_data.get('created_utc'))
        post_id = post_data.get('reddit_id', 'unknown')
        subreddit = post_data.get('subreddit', 'unknown')
        
        # Build formatted post
        formatted_post = f"📝 **POST** r/{subreddit} by u/{author} ({score} points, {created_date})\n"
        formatted_post += f"**{title}**\n"
        
        if content and content.strip():
            formatted_post += f"\n{content}"
        
        formatted_post += f"\n\n[Post ID: {post_id}]"
        
        return formatted_post
    
    def format_comment_thread(self, comments: List[Dict[str, Any]]) -> str:
        """
        Format comments in threaded, hierarchical order.
        
        Args:
            comments: List of comment dictionaries
        
        Returns:
            Formatted comments string
        """
        if not comments:
            return ""
        
        # Sort comments by depth and position to maintain thread structure
        sorted_comments = sorted(comments, key=lambda c: (c.get('depth', 0), c.get('position', 0)))
        
        formatted_comments = ["💬 **COMMENTS:**"]
        
        for comment in sorted_comments:
            formatted_comment = self.format_single_comment(comment)
            formatted_comments.append(formatted_comment)
        
        return "\n\n".join(formatted_comments)
    
    def format_single_comment(self, comment_data: Dict[str, Any]) -> str:
        """
        Format a single comment with proper indentation and metadata.
        
        Args:
            comment_data: Comment data dictionary
        
        Returns:
            Formatted comment string
        """
        content = comment_data.get('content', '')
        author = comment_data.get('author', 'Unknown')
        score = comment_data.get('score', 0)
        created_date = self._format_date(comment_data.get('created_utc'))
        depth = comment_data.get('depth', 0)
        comment_id = comment_data.get('reddit_id', 'unknown')
        is_root = comment_data.get('is_root', True)
        
        # Create indentation based on comment depth
        indent = "  " * depth
        
        # Comment type indicator
        comment_type = "↳" if depth > 0 else "→"
        
        # Build formatted comment
        formatted_comment = f"{indent}{comment_type} u/{author} ({score} points, {created_date})\n"
        formatted_comment += f"{indent}   {content}\n"
        formatted_comment += f"{indent}   [Comment ID: {comment_id}]"
        
        return formatted_comment
    
    def format_search_results_summary(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Format search results into a summary for LLM context.
        
        Args:
            search_results: List of search result dictionaries
        
        Returns:
            Formatted summary string
        """
        if not search_results:
            return "No relevant discussions found."
        
        summary_parts = [f"Found {len(search_results)} relevant discussions:\n"]
        
        for i, result in enumerate(search_results, 1):
            content_type = result.get('content_type', 'unknown').title()
            author = result.get('metadata', {}).get('author', 'Unknown')
            score = result.get('metadata', {}).get('score', 0)
            relevance = result.get('relevance_score', 0.0)
            preview = result.get('content_text', '')[:100] + "..." if len(result.get('content_text', '')) > 100 else result.get('content_text', '')
            
            summary_parts.append(
                f"{i}. {content_type} by u/{author} (Score: {score}, Relevance: {relevance:.2f})\n"
                f"   Preview: {preview}"
            )
        
        return "\n".join(summary_parts)
    
    def format_content_for_context_window(self, content: str, max_length: int = 2000) -> str:
        """
        Truncate content to fit within context windows while preserving structure.
        
        Args:
            content: Full content string
            max_length: Maximum character length
        
        Returns:
            Truncated content with preservation of structure
        """
        if len(content) <= max_length:
            return content
        
        # Try to truncate at natural break points
        truncated = content[:max_length]
        
        # Find last complete sentence or paragraph
        last_period = truncated.rfind('.')
        last_newline = truncated.rfind('\n\n')
        
        # Use the better break point
        break_point = max(last_period, last_newline)
        
        if break_point > max_length * 0.7:  # Only use if it's not too short
            truncated = content[:break_point + 1]
        
        # Add truncation indicator
        if len(content) > len(truncated):
            truncated += "\n\n[... content truncated for length ...]"
        
        return truncated
    
    def format_keyword_mentions_in_context(self, content: str, keywords: List[str]) -> str:
        """
        Highlight keyword mentions within content for better LLM focus.
        
        Args:
            content: Content string
            keywords: List of keywords to highlight
        
        Returns:
            Content with highlighted keywords
        """
        highlighted_content = content
        
        for keyword in keywords:
            # Simple case-insensitive highlighting
            import re
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted_content = pattern.sub(f"**{keyword.upper()}**", highlighted_content)
        
        return highlighted_content
    
    def _format_date(self, created_utc: Optional[int]) -> str:
        """Format Unix timestamp to readable date."""
        if not created_utc:
            return "unknown date"
        
        try:
            dt = datetime.fromtimestamp(created_utc)
            return dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, OSError):
            return "invalid date"
    
    def format_analytics_with_examples(self, analytics_data: Dict[str, Any], 
                                     examples: List[Dict[str, Any]]) -> str:
        """
        Combine analytics data with real content examples.
        
        Args:
            analytics_data: Structured analytics information
            examples: List of actual Reddit discussions that illustrate the patterns
        
        Returns:
            Combined analytical and contextual information
        """
        formatted_parts = []
        
        # Add analytics overview
        formatted_parts.append("📊 **ANALYTICS OVERVIEW**")
        formatted_parts.append(str(analytics_data))
        
        # Add real examples
        if examples:
            formatted_parts.append("\n🗣️ **ACTUAL DISCUSSIONS**")
            formatted_parts.append("Here are real examples from the data that illustrate these patterns:")
            
            for i, example in enumerate(examples[:3], 1):  # Limit to top 3 examples
                formatted_parts.append(f"\n**Example {i}:**")
                if example.get('post'):
                    formatted_parts.append(self.format_discussion_thread(example))
                else:
                    # Single comment example
                    formatted_parts.append(self.format_single_comment(example))
        
        return "\n".join(formatted_parts)


# Global content formatter instance
content_formatter = ContentFormatter()
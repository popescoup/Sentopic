"""
CLI Interface Package

Command-line interface components for analytics and LLM features.
Collection management remains in main.py as originally implemented.
"""

from .analytics import handle_analytics_commands
from .llm import handle_llm_commands

__all__ = ['handle_analytics_commands', 'handle_llm_commands']
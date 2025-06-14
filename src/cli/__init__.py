"""
CLI Interface Package

Command-line interface components for analytics.
Collection management remains in main.py as originally implemented.
"""

from .analytics import handle_analytics_commands

__all__ = ['handle_analytics_commands']
"""
Conversational AI Interface Module

This module provides a natural language interface to all business logic features.
It wraps existing API endpoints with conversational intelligence.

Main Components:
- intent_classifier: Maps natural language to API endpoints
- response_generator: Formats API responses conversationally
- conversation_state: Manages conversation context
- prompts: Response templates and patterns
"""

from .intent_classifier import classify_intent, extract_parameters
from .response_generator import generate_response, format_insights
from .conversation_state import ConversationState, get_conversation_state, save_conversation_state

__all__ = [
    'classify_intent',
    'extract_parameters',
    'generate_response',
    'format_insights',
    'ConversationState',
    'get_conversation_state',
    'save_conversation_state',
]

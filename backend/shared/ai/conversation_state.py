"""
Conversation State Management

Tracks conversation context for follow-up questions and maintains session history.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json


class ConversationState:
    """
    Manages conversation state for a single session.

    Attributes:
        session_id: Unique session identifier
        history: List of conversation turns
        context: Current context (last API call, last intent, etc.)
        created_at: Session creation timestamp
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: List[Dict] = []
        self.context: Dict = {}
        self.created_at = datetime.now().isoformat()

    def add_turn(self, user_query: str, intent: Dict, api_response: Dict, ai_response: Dict):
        """
        Add a conversation turn to history.

        Args:
            user_query: User's natural language question
            intent: Classified intent
            api_response: Raw API response
            ai_response: Generated conversational response
        """
        turn = {
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "intent": intent["intent"],
            "endpoint": intent["endpoint"],
            "response_summary": ai_response.get("answer", "")[:100],  # First 100 chars
        }
        self.history.append(turn)

        # Update context with last API call
        self.context = {
            "last_intent": intent["intent"],
            "last_endpoint": intent["endpoint"],
            "last_category": intent["category"],
            "last_data": api_response.get("data", {}),
            "turn_count": len(self.history)
        }

    def get_last_intent(self) -> Optional[str]:
        """Get the last classified intent."""
        return self.context.get("last_intent")

    def get_last_endpoint(self) -> Optional[str]:
        """Get the last API endpoint called."""
        return self.context.get("last_endpoint")

    def get_last_data(self) -> Dict:
        """Get data from last API response."""
        return self.context.get("last_data", {})

    def get_history(self, limit: int = 10) -> List[Dict]:
        """
        Get conversation history.

        Args:
            limit: Maximum number of turns to return

        Returns:
            List of recent conversation turns
        """
        return self.history[-limit:] if len(self.history) > limit else self.history

    def to_dict(self) -> Dict:
        """Serialize state to dictionary."""
        return {
            "session_id": self.session_id,
            "history": self.history,
            "context": self.context,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ConversationState":
        """Deserialize state from dictionary."""
        state = cls(data["session_id"])
        state.history = data.get("history", [])
        state.context = data.get("context", {})
        state.created_at = data.get("created_at", datetime.now().isoformat())
        return state


# In-memory session storage (for MVP)
# In production, replace with Redis or database
_sessions: Dict[str, ConversationState] = {}


def get_conversation_state(session_id: str) -> ConversationState:
    """
    Get or create conversation state for session.

    Args:
        session_id: Unique session identifier

    Returns:
        ConversationState instance
    """
    if session_id not in _sessions:
        _sessions[session_id] = ConversationState(session_id)
    return _sessions[session_id]


def save_conversation_state(state: ConversationState):
    """
    Save conversation state to storage.

    Args:
        state: ConversationState instance
    """
    _sessions[state.session_id] = state


def clear_conversation_state(session_id: str):
    """
    Clear conversation state for session.

    Args:
        session_id: Session to clear
    """
    if session_id in _sessions:
        del _sessions[session_id]


def get_all_sessions() -> List[str]:
    """Get list of all active session IDs."""
    return list(_sessions.keys())


def cleanup_old_sessions(max_age_hours: int = 24):
    """
    Clean up sessions older than max_age_hours.

    Args:
        max_age_hours: Maximum age in hours to keep sessions
    """
    from datetime import timedelta

    now = datetime.now()
    to_delete = []

    for session_id, state in _sessions.items():
        created = datetime.fromisoformat(state.created_at)
        age = now - created

        if age > timedelta(hours=max_age_hours):
            to_delete.append(session_id)

    for session_id in to_delete:
        del _sessions[session_id]

    return len(to_delete)

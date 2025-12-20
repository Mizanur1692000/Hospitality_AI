"""
Conversational AI API Endpoint

Natural language interface to all business logic features.
Wraps existing API endpoints with conversational intelligence.

Example Usage:
    POST /api/agent/conversational
    {
        "query": "What are my highest selling items?",
        "session_id": "user_123"
    }

Returns:
    {
        "status": "success",
        "data": {
            "answer": "Your top 3 best-selling items are...",
            "insights": ["Key insight 1", "Key insight 2"],
            "suggestions": ["Show me pricing opportunities", ...]
        }
    }
"""

from typing import Dict, Tuple
import uuid

from backend.shared.ai import (
    classify_intent,
    extract_parameters,
    generate_response,
    get_conversation_state,
    save_conversation_state
)
from backend.shared.utils.common import success_payload, error_payload

# Import existing business logic endpoints
from backend.consulting_services.menu import product_mix, pricing, design, menu_questions


def run(params: dict, file_bytes: bytes | None = None) -> Tuple[dict, int]:
    """
    Main conversational AI endpoint.

    Args:
        params: {
            "query": str,              # Natural language question (REQUIRED)
            "session_id": str,         # Session ID (optional, auto-generated if not provided)
        }
        file_bytes: Not used for conversational AI

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "conversational", "ai"

    try:
        # STEP 1: Extract and validate query
        query = params.get("query", "").strip()
        if not query:
            return error_payload(
                service,
                subtask,
                "Query parameter is required. Example: {'query': 'What are my highest selling items?'}",
                400
            )

        # Get or create session
        session_id = params.get("session_id")
        if not session_id:
            session_id = f"session_{uuid.uuid4().hex[:8]}"

        # STEP 2: Classify intent
        intent = classify_intent(query)

        if intent["confidence"] < 0.1 and intent["intent"] != "help":
            # Very low confidence - suggest help
            return success_payload(
                service,
                subtask,
                params,
                {
                    "answer": "I'm not sure I understood that. Here's what I can help with:",
                    "insights": [
                        "Try asking: 'What are my highest selling items?'",
                        "Or: 'Show me underpriced items'",
                        "Or: 'What are my star items?'"
                    ],
                    "suggestions": ["help", "Show me my menu analysis"],
                    "data_summary": {},
                    "session_id": session_id,
                    "debug": {
                        "classified_intent": intent["intent"],
                        "confidence": intent["confidence"]
                    }
                },
                []
            ), 200

        # STEP 3: Handle system intents (help, etc.)
        if intent["category"] == "system":
            response = generate_response(intent, {}, query)
            response["session_id"] = session_id
            return success_payload(service, subtask, params, response, []), 200

        # STEP 4: Extract parameters from query
        extracted_params = extract_parameters(query, intent)

        # STEP 5: Call appropriate business logic API
        api_response, status_code = _call_api_endpoint(intent["endpoint"], extracted_params)

        if status_code != 200:
            return api_response, status_code

        # STEP 6: Generate conversational response
        conversational_response = generate_response(intent, api_response, query)

        # Add session ID
        conversational_response["session_id"] = session_id

        # Add original API data for advanced users (optional)
        conversational_response["raw_data"] = api_response.get("data", {})

        # STEP 7: Update conversation state
        state = get_conversation_state(session_id)
        state.add_turn(query, intent, api_response, conversational_response)
        save_conversation_state(state)

        # Add conversation metadata
        conversational_response["conversation_metadata"] = {
            "turn_count": len(state.history),
            "last_intent": intent["intent"],
            "endpoint_called": intent["endpoint"]
        }

        # STEP 8: Return success with conversational response
        return success_payload(
            service,
            subtask,
            params,
            conversational_response,
            []  # No recommendations - suggestions are in conversational_response
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Conversational AI error: {str(e)}", 500)


def _call_api_endpoint(endpoint: str, params: dict) -> Tuple[dict, int]:
    """
    Call the appropriate business logic API endpoint.

    Args:
        endpoint: Endpoint path (e.g., "menu/product_mix")
        params: Parameters to pass to endpoint

    Returns:
        Tuple of (api_response, status_code)
    """
    # Map endpoint strings to actual functions
    endpoint_map = {
        "menu/product_mix": product_mix.run,
        "menu/pricing": pricing.run,
        "menu/design": design.run,
        "menu/questions": menu_questions.run,
    }

    if endpoint not in endpoint_map:
        return error_payload(
            "conversational",
            "ai",
            f"Unknown endpoint: {endpoint}",
            500
        ), 500

    # Call the endpoint
    api_function = endpoint_map[endpoint]
    return api_function(params, None)


def get_conversation_history(params: dict, file_bytes: bytes | None = None) -> Tuple[dict, int]:
    """
    Get conversation history for a session.

    Args:
        params: {
            "session_id": str,  # Required
            "limit": int        # Optional, default 10
        }

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "conversational", "history"

    try:
        session_id = params.get("session_id")
        if not session_id:
            return error_payload(service, subtask, "session_id is required", 400)

        limit = params.get("limit", 10)

        state = get_conversation_state(session_id)
        history = state.get_history(limit)

        return success_payload(
            service,
            subtask,
            params,
            {
                "session_id": session_id,
                "history": history,
                "turn_count": len(state.history),
                "created_at": state.created_at
            },
            []
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Error retrieving history: {str(e)}", 500)


def clear_conversation(params: dict, file_bytes: bytes | None = None) -> Tuple[dict, int]:
    """
    Clear conversation history for a session.

    Args:
        params: {
            "session_id": str  # Required
        }

    Returns:
        Tuple of (response_dict, status_code)
    """
    from backend.shared.ai.conversation_state import clear_conversation_state

    service, subtask = "conversational", "clear"

    try:
        session_id = params.get("session_id")
        if not session_id:
            return error_payload(service, subtask, "session_id is required", 400)

        clear_conversation_state(session_id)

        return success_payload(
            service,
            subtask,
            params,
            {
                "message": f"Conversation cleared for session {session_id}",
                "session_id": session_id
            },
            []
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Error clearing conversation: {str(e)}", 500)

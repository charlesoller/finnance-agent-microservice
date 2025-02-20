"""Format History Function"""

from typing import List

from .types import ChatMessage, FormattedChatMessage


def format_history(history: List[ChatMessage]) -> List[FormattedChatMessage]:
    """Formats chat log history for ChatGPT context"""
    formatted = []
    for message in history:
        role: str = message["message_type"].lower()
        if role == "ai":
            role = "assistant"
        formatted.append({"role": role, "content": message["message_content"]})
    return formatted

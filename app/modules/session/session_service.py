"""This module contains all functionality needed for sessions"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.utils import SUMMARY_PROMPT, FormattedChatMessage


class SessionService:
    """This class contains all functionality relevant to sessions"""

    def __init__(self, db, openai):
        self.__db = db
        self.__openai = openai

    def update_session(
        self,
        session_id: str,
        history: List[FormattedChatMessage],
        is_first_message: bool,
    ):
        """This method is responsible for updating session info"""
        if is_first_message:
            return self.__create_new_session(session_id=session_id, history=history)

        timestamp = datetime.now(timezone.utc).isoformat()
        item_count = len(history)
        updating_name = False
        session_name = ""

        curr_session = self.__db.get_item(
            Key={"session_id": session_id},
            ProjectionExpression="last_updated_count, session_name",
        )

        item = curr_session.get("Item", {})
        last_updated_count = item.get("last_updated_count", 0)

        if 8 > last_updated_count <= item_count:
            # Update the title after 8 messages
            session_name = self.__generate_session_name(history)
            updating_name = True

        update_args = {
            ":updated_at": timestamp,
            ":item_count": item_count,
            ":last_updated_count": item_count if updating_name else last_updated_count,
        }

        update_expression = """
        SET updated_at = :updated_at,
        item_count = :item_count,
        last_updated_count = :last_updated_count
        """

        if updating_name:
            update_expression += ", session_name = :session_name"
            update_args[":session_name"] = session_name

        try:
            updated_item = self.__db.update_item(
                Key={"session_id": str(session_id)},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=update_args,
            )
            return updated_item
        except Exception as e:
            raise RuntimeError(f"Failed to update session: {e}") from e

    def __create_new_session(
        self, session_id: str, history: List[FormattedChatMessage]
    ):
        timestamp = datetime.now(timezone.utc).isoformat()
        session_name = self.__generate_session_name(history)

        item = {
            "session_id": str(session_id),
            "session_name": str(session_name),
            "created_at": str(timestamp),
            "updated_at": str(timestamp),
            "last_updated_count": len(history),
            "item_count": len(history),
        }

        self.__db.put_item(Item=item)

    def __generate_session_name(self, history: List[FormattedChatMessage]):
        params: Dict[str, Any] = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "developer", "content": SUMMARY_PROMPT},
                *history,
            ],
            "response_format": {"type": "json_object"},
        }

        completion = self.__openai.chat.completions.create(**params)

        response = completion.choices[0].message.content
        json_completion = json.loads(response)
        name = str(json_completion["title"])

        return name

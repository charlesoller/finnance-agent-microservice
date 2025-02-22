"""Contains all agent functionality"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi.responses import StreamingResponse

from src.utils import (
    ChatMessage,
    GraphResponse,
    MessageOwner,
    FormattedMessageOwner,
    format_history
)

class AgentService:
    """This class contains the functionality for the OpenAI chat completions"""

    def __init__(self, openai, instructions, model, tools, db, session_service):
        self.__openai = openai
        self.__system_prompt = instructions
        self.__model = model
        self.__tools = tools
        self.__db = db
        self.__session_service = session_service

    async def handle_message(
        self, message: str, history: List[ChatMessage], user_id: str, session_id: str
    ):
        """Saves user message and returns generator as StreamingResponse"""
        await self.__save_message(
            user_id=user_id,
            session_id=session_id,
            message_type=MessageOwner.USER,
            message_content=message,
        )

        is_first_message = len(history) == 0
        updated_history = format_history(history)
        updated_history.append({
            "role": FormattedMessageOwner.USER,
            "content": message
        })

        self.__session_service.update_session(
            session_id=session_id, history=updated_history, is_first_message=is_first_message
        )

        return StreamingResponse(
            self.__generate_response(message, history, user_id, session_id),
            media_type="text/event-stream",
        )

    async def __generate_response(
        self, message: str, history: List[ChatMessage], user_id: str, session_id: str
    ):
        """
        Acts as async generator to return chunks from openai completion. Also saves AI response.
        """
        full_response = ""

        response_stream = await self.__openai.chat.completions.create(
            **self.__get_params(
                message=message,
                history=history,
            )
        )

        async for chunk in response_stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                yield f"data: {json.dumps({'content': content})}\n\n"

        dict_response = json.loads(full_response)

        await self.__save_message(
            user_id=user_id,
            session_id=session_id,
            message_type=MessageOwner.AI,
            message_content=dict_response.get("message", ""),
            graph_data=dict_response.get("graph", None)
        )

        yield "data: [DONE]\n\n"

    async def __save_message(
        self,
        user_id: str,
        session_id: str,
        message_type: MessageOwner,
        message_content: str,
        graph_data: Optional[GraphResponse] = None,
    ):
        """This method is responsible for saving chats to the database"""
        timestamp = datetime.now(timezone.utc).isoformat()
        item = {
            "message_id": str(uuid.uuid4()),
            "user_id": str(user_id),
            "session_id": str(session_id),
            "message_type": str(message_type.value),
            "message_content": str(message_content),
            "timestamp": str(timestamp),
        }

        if graph_data:
            item["graph_data"] = json.dumps(graph_data)

        self.__db.put_item(Item=item)
        return item

    def __get_params(self, history: List[ChatMessage], message: str):
        """Returns params for Completion API call"""
        params: Dict[str, Any] = {
            "model": self.__model,
            "messages": [
                {"role": "developer", "content": self.__system_prompt},
                *format_history(history),
                {"role": "user", "content": message},
            ],
            "response_format": {"type": "json_object"},
            "tools": self.__tools,
            "stream": True,
        }

        return params

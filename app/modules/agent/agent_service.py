"""Contains all agent functionality"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi.responses import StreamingResponse

from app.utils import (
    ChatMessage,
    FormattedMessageOwner,
    GraphResponse,
    MessageOwner,
    calculate_compound_interest,
    format_history,
    get_acct_details,
    get_transaction_details,
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
        self,
        message: str,
        history: List[ChatMessage],
        user_id: str,
        session_id: str,
        context: Optional[List[str]] = None,
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
        updated_history.append({"role": FormattedMessageOwner.USER, "content": message})

        self.__session_service.update_session(
            session_id=session_id,
            history=updated_history,
            is_first_message=is_first_message,
        )

        return StreamingResponse(
            self.__generate_response(
                message=message,
                history=history,
                user_id=user_id,
                session_id=session_id,
                context=context,
            ),
            media_type="text/event-stream",
        )

    # pylint: disable=R0912
    async def __generate_response(
        self,
        message: str,
        history: List[ChatMessage],
        user_id: str,
        session_id: str,
        context: Optional[List[str]] = None,
    ):
        """
        Acts as async generator to yield chunks from openai completion and handles tool calls.
        Context is only maintained within a single chain of tool calls, not between separate messages.

        Args:
            message (str): The user's message or tool context message
            history (List[ChatMessage]): Chat history
            user_id (str): User identifier
            session_id (str): Session identifier
            context (List[str]): List of context strings from tool calls or user supplied info in the current chain
        """
        print(f"\nRunning with message: {message}")
        if context:
            print(f"Current tool chain context: {context}\n")

        full_response = ""
        final_tool_calls = {}

        # Only combine tool context with the message if we're in a tool chain
        context_str = ""
        enhanced_message = message
        if context:
            context_str = " ".join(context)

        if len(context_str) > 0:
            enhanced_message = (
                f"Based on this context: {context_str}\n\n"
                f"Please provide a response to the original question: {message}"
            )

        response_stream = await self.__openai.responses.create(
            **self.__get_params(
                message=enhanced_message,
                history=history,
            )
        )

        async for chunk in response_stream:
            print(f"\nChunk Type: {chunk.type}\n")

            if chunk.type == "response.output_item.added":
                print(f"Test Chunk: {chunk}")
                item = chunk.item
                index = chunk.output_index
                if item and item.type == "function_call":
                    function_name = item.name
                    final_tool_calls[index] = {
                        "function": {"name": function_name, "arguments": ""}
                    }

            if chunk.type == "response.function_call_arguments.delta":
                # Handles custom tool call chunks
                print(f"Tool Chunk: {chunk}\n\n")
                index = chunk.output_index
                content = chunk.delta
                # Correctly append to the arguments string
                if index in final_tool_calls:
                    final_tool_calls[index]["function"]["arguments"] += content

            if chunk.type == "response.output_text.delta":
                # Handles text response
                print(f"\nText Chunk: {chunk} \n")
                content = chunk.delta
                full_response += content
                yield f"data: {json.dumps({'content': content})}\n\n"

        if final_tool_calls:
            print(f"\nProcessing tools in current chain: {final_tool_calls}")
            current_chain_context = (
                context.copy() if context is not None else []
            )  # Keep context only within this chain

            for index, tool_call in final_tool_calls.items():
                function_name = tool_call["function"]["name"]
                try:
                    arguments = json.loads(tool_call["function"]["arguments"])
                    tool_result = await self.__execute_tool(function_name, arguments)
                    print(f"\nTool results: {tool_result}\n")

                    if tool_result:
                        # Add new tool result to the current chain's context
                        current_chain_context.append(
                            f"Result from {function_name}: {str(tool_result)}"
                        )

                        # Recursive call with current chain's context
                        async for response_chunk in self.__generate_response(
                            message=message,  # Keep original message
                            history=history,
                            user_id=user_id,
                            session_id=session_id,
                            context=current_chain_context,
                        ):
                            yield response_chunk

                except json.JSONDecodeError:
                    print(
                        f"Failed to parse tool arguments: {tool_call['function']['arguments']}"
                    )
                    continue

        # Only save and finish when we have no more tool calls
        if not final_tool_calls:
            try:
                # First try to parse as JSON in case the response is structured
                dict_response = json.loads(full_response)
                final_message = dict_response.get("message", "")
                print(f"\nFinal message with no more tool calls: {final_message}\n")
                if final_message:
                    await self.__save_message(
                        user_id=user_id,
                        session_id=session_id,
                        message_type=MessageOwner.AI,
                        message_content=final_message,
                        graph_data=dict_response.get("graph", None),
                    )
            except json.JSONDecodeError:
                # If it's not valid JSON, just use the raw response as the message
                print(f"\nFinal message (not JSON): {full_response}\n")
                if full_response:
                    await self.__save_message(
                        user_id=user_id,
                        session_id=session_id,
                        message_type=MessageOwner.AI,
                        message_content=full_response,
                        graph_data=None,
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
            "instructions": self.__system_prompt,
            "input": [
                # {"role": "developer", "content": self.__system_prompt},
                *format_history(history),
                {"role": "user", "content": message},
            ],
            # "text": {
            #     "format": {"type": "json_object"}
            # },
            # "response_format": {"type": "json_object"},
            "tools": self.__tools,
            "tool_choice": "auto",
            "stream": True,
            "max_output_tokens": 4096,
        }

        return params

    async def __execute_tool(self, function_name, args):
        """
        Execute the tool function based on its name and arguments.
        """
        if function_name == "calculate_compound_interest":
            return calculate_compound_interest(**args)
        if function_name == "get_acct_details":
            return get_acct_details(**args)
        if function_name == "get_transaction_details":
            return get_transaction_details(**args)

        return f"Unknown function: {function_name}"

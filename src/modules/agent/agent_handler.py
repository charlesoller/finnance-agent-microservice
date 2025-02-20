"""Handles all incoming requests to agent"""

from fastapi import APIRouter


class AgentHandler:
    """Handles requests to agent service"""

    def __init__(self, agent_service):
        self.router = APIRouter(prefix="/agent", tags=["agent"])
        self.__agent_service = agent_service
        self.__setup_routes()

    def __setup_routes(self):
        """Initializes all routes"""
        self.router.post("/execute")(self.execute_agent)

    async def execute_agent(self, payload: dict):
        """Handles agent execution"""
        message = payload.get("message_content", "")
        history = payload.get("history", [])
        session_id = payload.get("session_id", "")
        user_id = payload.get("user_id", "")

        return await self.__agent_service.handle_message(
            message=message, history=history, session_id=session_id, user_id=user_id
        )

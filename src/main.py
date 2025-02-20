"""Server entry point. Also responsible for config."""

import logging
import os

import boto3
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

from src.modules import AgentHandler, AgentService
from src.utils import AGENT_INSTRUCTIONS, AGENT_MODEL, AGENT_TOOLS

load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai = AsyncOpenAI(api_key=OPENAI_API_KEY)

if os.getenv("ENV") == "local":
    logger.info(f"Connecting to local DynamoDB at: {DYNAMODB_ENDPOINT}")
    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url=DYNAMODB_ENDPOINT,
        region_name="us-east-1",
        aws_access_key_id="dummy",
        aws_secret_access_key="dummy",
    )
else:
    dynamodb = boto3.resource("dynamodb")

CHAT_LOGS_TABLE_NAME = "chat_logs"
SESSION_INFO_TABLE_NAME = "session_info"

chat_logs_db = dynamodb.Table(CHAT_LOGS_TABLE_NAME)
session_info_db = dynamodb.Table(SESSION_INFO_TABLE_NAME)

agent_service = AgentService(
    openai=openai,
    instructions=AGENT_INSTRUCTIONS,
    model=AGENT_MODEL,
    tools=AGENT_TOOLS,
    db=chat_logs_db,
)
agent_handler = AgentHandler(agent_service=agent_service)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_handler.router)


@app.get("/")
async def root():
    """Test Hello World route"""
    return {"message": "Hello World"}

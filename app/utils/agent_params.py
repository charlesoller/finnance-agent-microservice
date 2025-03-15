# pylint: skip-file
"""Consts for all agent params"""

from app.utils.prompts import AGENT_PROMPT

AGENT_INSTRUCTIONS = AGENT_PROMPT
AGENT_MODEL = "gpt-4o-mini"
AGENT_TOOLS = [
    {"type": "web_search_preview"},
    {
        "type": "function",
        "name": "calculate_compound_interest",
        "description": "Calculate compound interest with optional periodic contributions for investment planning.",
        "parameters": {
            "type": "object",
            "properties": {
                "principal": {
                    "type": "number",
                    "description": "Initial investment amount",
                },
                "annual_rate": {
                    "type": "number",
                    "description": "Annual interest rate as a percentage (e.g., 5 for 5%)",
                },
                "time_years": {
                    "type": "number",
                    "description": "Investment time period in years (can be fractional)",
                },
                "compounds_per_year": {
                    "type": ["integer", "string"],
                    "description": "Number of times interest compounds per year or one of: 'daily', 'monthly', 'quarterly', 'semi-annually', 'annually'",
                },
                "additional_contribution": {
                    "type": ["number", "null"],
                    "description": "Additional periodic contribution amount",
                },
                "contribution_frequency": {
                    "type": ["string", "null"],
                    "enum": ["monthly", "quarterly", "annually"],
                    "description": "Frequency of additional contributions",
                },
                "rounding_decimals": {
                    "type": ["integer", "null"],
                    "description": "Number of decimal places to round results to",
                },
            },
            "required": [
                "principal",
                "annual_rate",
                "time_years",
                "compounds_per_year",
                "additional_contribution",
                "contribution_frequency",
                "rounding_decimals",
            ],
            "additionalProperties": False,
            "strict": True,
        },
    },
    {
        "type": "function",
        "name": "get_acct_details",
        "description": "Retrieve detailed account information for multiple accounts from the financial connections API.",
        "parameters": {
            "type": "object",
            "properties": {
                "acct_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "A list of unique identifiers for the accounts to retrieve details for.",
                }
            },
            "required": ["acct_ids"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_transaction_details",
        "description": "Retrieve detailed transaction information for multiple transactions from the financial connections API.",
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "A list of unique identifiers for the transactions to retrieve details for.",
                }
            },
            "required": ["transaction_ids"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

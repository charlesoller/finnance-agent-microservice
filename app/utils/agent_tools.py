# pylint: skip-file
"""The functions provided to the AI agent"""

import os
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, Literal, Union

import requests
from dotenv import load_dotenv
import logging
import traceback


def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    time_years: float,
    compounds_per_year: Union[
        int, Literal["daily", "monthly", "quarterly", "semi-annually", "annually"]
    ] = 12,
    additional_contribution: float = 0,
    contribution_frequency: Literal["monthly", "quarterly", "annually"] = "monthly",
    rounding_decimals: int = 2,
) -> Dict[str, Union[float, Dict[int, float]]]:
    """
    Calculate compound interest with optional periodic contributions.

    Args:
        principal: Initial investment amount
        annual_rate: Annual interest rate as a percentage (e.g., 5 for 5%)
        time_years: Investment time period in years (can be fractional)
        compounds_per_year: Number of times interest compounds per year
            Can be an integer or one of: 'daily', 'monthly', 'quarterly', 'semi-annually', 'annually'
        additional_contribution: Additional periodic contribution amount
        contribution_frequency: Frequency of additional contributions
        rounding_decimals: Number of decimal places to round results to

    Returns:
        Dict containing:
        - total_amount: Final balance after compound interest
        - interest_earned: Total interest earned
        - contributions_total: Total amount contributed
        - yearly_breakdown: Dict of year-by-year balances

    Raises:
        ValueError: If input parameters are invalid
    """
    # Input validation
    if principal < 0 or annual_rate < 0 or time_years <= 0:
        raise ValueError("Principal, rate, and time must be positive numbers")

    # Optionals handling
    if not compounds_per_year:
        compounds_per_year = 12
    if not additional_contribution:
        additional_contribution = 0
    if not contribution_frequency:
        contribution_frequency = "monthly"
    if not rounding_decimals:
        rounding_decimals = 2

    # Convert annual_rate to decimal
    rate = annual_rate / 100

    # Convert string compound frequencies to numbers
    compounds_mapping = {
        "daily": 365,
        "monthly": 12,
        "quarterly": 4,
        "semi-annually": 2,
        "annually": 1,
    }

    if isinstance(compounds_per_year, str):
        if compounds_per_year not in compounds_mapping:
            raise ValueError(
                f"Invalid compounding frequency. Must be one of {list(compounds_mapping.keys())}"
            )
        compounds_per_year = compounds_mapping[compounds_per_year]

    # Convert contribution frequency to number of contributions per year
    contribution_mapping = {"monthly": 12, "quarterly": 4, "annually": 1}
    contributions_per_year = contribution_mapping[contribution_frequency]

    # Initialize tracking variables
    yearly_breakdown = {}
    total = Decimal(str(principal))
    total_contributions = Decimal(str(principal))

    # Calculate compound interest year by year
    for year in range(1, int(time_years) + 1):
        # Compound interest on existing balance
        total *= (1 + Decimal(str(rate)) / compounds_per_year) ** compounds_per_year

        # Add periodic contributions
        contribution_amount = Decimal(additional_contribution) * contributions_per_year
        total += contribution_amount
        total_contributions += contribution_amount

        # Store yearly balance
        yearly_breakdown[year] = float(
            total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )

    # Handle partial final year if time_years is not a whole number
    if time_years % 1 > 0:
        remaining_time = time_years % 1
        # Compound interest for partial year
        total *= (1 + Decimal(str(rate)) / Decimal(str(compounds_per_year))) ** (
            Decimal(str(compounds_per_year)) * Decimal(str(remaining_time))
        )
        # Add contributions for partial year
        partial_contributions = (
            Decimal(str(additional_contribution))
            * Decimal(str(contributions_per_year))
            * Decimal(str(remaining_time))
        )
        total += partial_contributions
        total_contributions += partial_contributions
        yearly_breakdown[int(time_years) + 1] = float(
            total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )

    # Prepare results
    final_amount = float(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    interest_earned = final_amount - float(total_contributions)

    return {
        "total_amount": final_amount,
        "interest_earned": round(interest_earned, rounding_decimals),
        "contributions_total": float(total_contributions),
        "yearly_breakdown": yearly_breakdown,
    }


def get_acct_details(acct_ids: list[str]):
    """
    Retrieves detailed account information for multiple accounts from a financial connections API endpoint.

    Args:
        acct_ids (list[str]): A list of unique account IDs to retrieve details for.

    Returns:
        list[dict]: A list of JSON responses containing account details.

    Raises:
        requests.exceptions.HTTPError: If any API request fails.
        requests.exceptions.RequestException: For other request-related errors.
        OSError: If environment variables are not properly configured.
    """

    load_dotenv()
    API_URL = os.getenv("API_URL")

    if not API_URL:
        raise OSError("API_URL environment variable is not set.")

    headers = {"Content-Type": "application/json"}
    account_details = []

    for acct_id in acct_ids:
        url = f"{API_URL}/financial-connections/accounts/{acct_id}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Convert balance values from cents to dollars
            if "balance" in data:
                balance = data["balance"]
                if "cash" in balance and "available" in balance["cash"]:
                    balance["cash"]["available"]["usd"] /= 100
                if "current" in balance:
                    balance["current"]["usd"] /= 100

            account_details.append(data)
        else:
            response.raise_for_status()

    return account_details


def get_transaction_details(transaction_ids: list[str]):
    """
    Retrieves detailed account information for multiple transactions from a financial connections API endpoint.

    Args:
        transaction_ids (list[str]): A list of unique transaction IDs to retrieve details for.

    Returns:
        list[dict]: A list of JSON responses containing transaction details.

    Raises:
        requests.exceptions.HTTPError: If any API request fails.
        requests.exceptions.RequestException: For other request-related errors.
        OSError: If environment variables are not properly configured.
    """
    # Configure logging
    logger = logging.getLogger(__name__)
    
    try:
        load_dotenv()
        API_URL = os.getenv("API_URL")
        
        logger.info(f"API_URL: {API_URL}")
        
        if not API_URL:
            logger.error("API_URL environment variable is not set")
            raise OSError("API_URL environment variable is not set.")
            
        headers = {"Content-Type": "application/json"}
        transaction_details = []
        
        logger.info(f"Processing {len(transaction_ids)} transaction IDs")
        
        for transaction_id in transaction_ids:
            try:
                url = f"{API_URL}/financial-connections/transactions/{transaction_id}"
                logger.info(f"Making request to: {url}")
                
                response = requests.get(url, headers=headers, timeout=10)
                logger.info(f"Response status code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"Raw response data: {data}")
                    
                    # Convert balance values from cents to dollars
                    if "amount" in data:
                        data["amount"] /= 100
                        logger.debug(f"Converted amount to dollars: {data['amount']}")
                    
                    transaction_details.append(data)
                else:
                    logger.error(f"Request failed with status code: {response.status_code}")
                    logger.error(f"Response content: {response.text}")
                    response.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                logger.error(f"HTTP error for transaction ID {transaction_id}: {http_err}")
                logger.error(f"Response details: {response.text if 'response' in locals() else 'No response'}")
                raise
            except requests.exceptions.RequestException as req_err:
                logger.error(f"Request error for transaction ID {transaction_id}: {req_err}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error for transaction ID {transaction_id}: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise
                
        logger.info(f"Successfully retrieved details for {len(transaction_details)} transactions")
        return transaction_details
        
    except OSError as os_err:
        logger.error(f"OS Error: {os_err}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_transaction_details: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

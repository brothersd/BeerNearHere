# /utils/OAuth2.py
import requests
import base64
import os
import logging
from utils.config import CLIENT_ID, CLIENT_SECRET, AUTH_ENDPOINT

# Set up logging for easier debugging on EC2
logger = logging.getLogger(__name__)

def get_token():
    """
    Retrieves an OAuth2 access token from Kroger.
    Uses credentials managed by utils/config.py via environment variables.
    """
    # Safety check for credentials
    if not CLIENT_ID or not CLIENT_SECRET:
        logger.error("Kroger API credentials missing. Check your .env file.")
        return None

    # 1. Encode credentials for Basic Authentication
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()

    # 2. Prepare the Request
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_auth}"
    }
    
    # 'product.compact' provides access to basic product search and locations
    payload = "grant_type=client_credentials&scope=product.compact"

    try:
        response = requests.post(
            AUTH_ENDPOINT, 
            headers=headers, 
            data=payload, 
            timeout=10  # Prevents hanging on EC2 if the API is slow
        )
        
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            logger.error(f"Auth Failed: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Connection error during authentication: {e}")
        return None

# The testing block below only runs if you execute this file directly
if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"Success! Token starts with: {token[:15]}...")
    else:
        print("Failed to retrieve token. Check logs.")
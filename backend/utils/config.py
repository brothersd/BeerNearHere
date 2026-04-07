#/utils/config.py
import os

# Kroger API Credentials
CLIENT_ID = os.environ.get("KROGER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("KROGER_CLIENT_SECRET")
AUTH_ENDPOINT = "https://api.kroger.com/v1/connect/oauth2/token"

# Search radius in miles for store location services
search_radius = 25
import time
import requests
from config import JIRA_CLIENT_ID, JIRA_CLIENT_SECRET, JIRA_TOKEN_URL

# In-memory store (Reset on restart)
jira_tokens = {}

def save_tokens(user_id: str, tokens: dict):
    # Calculate expiration time (current time + expires_in seconds)
    tokens["expires_at"] = time.time() + tokens.get("expires_in", 3600)
    jira_tokens[user_id] = tokens

def refresh_jira_token(user_id: str):
    tokens = jira_tokens.get(user_id)
    if not tokens or "refresh_token" not in tokens:
        return None

    payload = {
        "grant_type": "refresh_token",
        "client_id": JIRA_CLIENT_ID,
        "client_secret": JIRA_CLIENT_SECRET,
        "refresh_token": tokens["refresh_token"]
    }

    response = requests.post(JIRA_TOKEN_URL, json=payload)
    if response.status_code == 200:
        new_tokens = response.json()
        # Ensure we don't lose the refresh token if the API doesn't return a new one
        if "refresh_token" not in new_tokens:
            new_tokens["refresh_token"] = tokens["refresh_token"]
        save_tokens(user_id, new_tokens)
        return new_tokens["access_token"]
    return None

def get_valid_token(user_id: str):
    tokens = jira_tokens.get(user_id)
    if not tokens:
        return None

    # Refresh if token is within 60 seconds of expiring
    if time.time() > (tokens["expires_at"] - 60):
        return refresh_jira_token(user_id)
    
    return tokens["access_token"]

def is_connected(user_id: str) -> bool:
    return user_id in jira_tokens
import time
import requests
from supabase import create_client, Client
from config import JIRA_CLIENT_ID, JIRA_CLIENT_SECRET, JIRA_TOKEN_URL, SUPABASE_URL, SUPABASE_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_tokens(user_id: str, tokens: dict):
    """Saves or updates tokens in the Supabase 'jira_tokens' table."""
    # Calculate expiration time
    expires_at = time.time() + tokens.get("expires_in", 3600)
    
    data = {
        "user_id": user_id,
        "access_token": tokens.get("access_token"),
        "refresh_token": tokens.get("refresh_token"),
        "expires_at": expires_at
    }
    
    # Upsert data: Update if user_id exists, otherwise insert
    supabase.table("jira_tokens").upsert(data).execute()

def refresh_jira_token(user_id: str):
    """Refreshes the Jira token and updates the Supabase record."""
    response = supabase.table("jira_tokens").select("*").eq("user_id", user_id).execute()
    user_data = response.data[0] if response.data else None

    if not user_data or not user_data.get("refresh_token"):
        return None

    payload = {
        "grant_type": "refresh_token",
        "client_id": JIRA_CLIENT_ID,
        "client_secret": JIRA_CLIENT_SECRET,
        "refresh_token": user_data["refresh_token"]
    }

    res = requests.post(JIRA_TOKEN_URL, json=payload)
    if res.status_code == 200:
        new_tokens = res.json()
        # Maintain the old refresh token if the API doesn't return a new one
        if "refresh_token" not in new_tokens:
            new_tokens["refresh_token"] = user_data["refresh_token"]
        
        save_tokens(user_id, new_tokens)
        return new_tokens["access_token"]
    return None

def get_valid_token(user_id: str):
    """Retrieves a valid token from Supabase, refreshing it if necessary."""
    response = supabase.table("jira_tokens").select("*").eq("user_id", user_id).execute()
    user_data = response.data[0] if response.data else None

    if not user_data:
        return None

    # Refresh if within 60 seconds of expiring
    if time.time() > (user_data["expires_at"] - 60):
        return refresh_jira_token(user_id)
    
    return user_data["access_token"]

def is_connected(user_id: str) -> bool:
    """Checks if a user has a record in Supabase."""
    response = supabase.table("jira_tokens").select("user_id").eq("user_id", user_id).execute()
    return len(response.data) > 0
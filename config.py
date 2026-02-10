import os
from dotenv import load_dotenv

load_dotenv()

# OAuth credentials
JIRA_CLIENT_ID = os.getenv("JIRA_CLIENT_ID")
JIRA_CLIENT_SECRET = os.getenv("JIRA_CLIENT_SECRET")

# OAuth redirect
JIRA_REDIRECT_URI = "http://localhost:8000/auth/jira/callback"

# Atlassian OAuth endpoints
JIRA_AUTH_URL = "https://auth.atlassian.com/authorize"
JIRA_TOKEN_URL = "https://auth.atlassian.com/oauth/token"

# Atlassian API base
JIRA_API_BASE_URL = "https://api.atlassian.com"

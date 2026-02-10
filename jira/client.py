import requests
from config import JIRA_API_BASE_URL


def jira_headers(access_token: str):
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

def get_issue(issue_key: str, access_token: str):
    url = f"{JIRA_API_BASE_URL}/rest/api/3/issue/{issue_key}"
    response = requests.get(url, headers=jira_headers(access_token))
    response.raise_for_status()
    return response.json()

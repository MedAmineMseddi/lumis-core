import requests
from config import JIRA_API_BASE_URL
from jira.client import jira_headers

def add_comment(issue_key: str, comment: str, access_token: str):
    url = f"{JIRA_API_BASE_URL}/rest/api/3/issue/{issue_key}/comment"

    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": comment}
                    ]
                }
            ]
        }
    }

    response = requests.post(
        url,
        headers=jira_headers(access_token),
        json=payload
    )
    response.raise_for_status()

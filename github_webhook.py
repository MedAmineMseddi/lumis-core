from fastapi import APIRouter, Request, HTTPException
import re
from jira.client import get_issue, get_accessible_resources
from jira.actions import add_comment, transition_issue
from logic.decision_engine import decide_jira_action
from token_store import get_valid_token

# Rename to github_router to fix the ImportError in main.py
github_router = APIRouter()

TASK_ID_REGEX = r"\b[A-Z]{2,10}-\d+\b"

def extract_issue_key(message: str):
    match = re.search(TASK_ID_REGEX, message)
    return match.group(0) if match else None

@github_router.post("/webhook/github")
async def github_webhook(request: Request):
    payload = await request.json()
    commits = payload.get("commits", [])
    
    # Using the temporary demo-user ID
    user_id = "demo-user" 
    access_token = get_valid_token(user_id)
    
    if not access_token:
        raise HTTPException(status_code=401, detail="User not connected or token expired")

    # Fetch accessible resources to get the cloud_id
    resources = get_accessible_resources(access_token)
    if not resources:
        return {"status": "no jira sites found"}
    cloud_id = resources[0]["id"]

    for commit in commits:
        message = commit["message"]
        issue_key = extract_issue_key(message)
        
        if not issue_key:
            continue

        try:
            issue = get_issue(cloud_id, issue_key, access_token)
            decision = decide_jira_action(issue, message)

            if decision:
                # Always add the comment
                add_comment(cloud_id, issue_key, decision["message"], access_token)
                
                # Perform transition if requested by the engine (e.g., for features)
                if decision.get("action") == "transition":
                    transition_issue(cloud_id, issue_key, decision["target_status"], access_token)
                        
        except Exception as e:
            print(f"Error processing {issue_key}: {e}")
            continue

    return {"status": "processed"}
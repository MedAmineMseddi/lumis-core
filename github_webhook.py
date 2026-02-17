from fastapi import APIRouter, Request, HTTPException
import re
from jira.client import get_issue, get_accessible_resources
from jira.actions import add_comment, transition_issue
from logic.decision_engine import decide_jira_action
from token_store import get_valid_token

# Fixed name to match main.py import
github_router = APIRouter()

# Supports JIRA (PROJ-123) and placeholder for Linear (LIN-123)
TASK_ID_REGEX = r"\b([A-Z]{2,10})-(\d+)\b"

def extract_tasks(message: str):
    """
    Layer 2: Task Extraction.
    Identifies task IDs and determines the platform.
    """
    match = re.search(TASK_ID_REGEX, message)
    if not match:
        return None
    
    full_id = match.group(0)
    prefix = match.group(1)
    
    # Logic to detect platform based on prefix
    # Future: Add Linear logic here
    platform = "jira" if prefix != "LIN" else "linear"
    
    return {"id": full_id, "platform": platform}

@github_router.post("/webhook/github")
async def github_webhook(request: Request):
    payload = await request.json()
    commits = payload.get("commits", [])
    
    user_id = "demo-user" 
    access_token = get_valid_token(user_id)
    
    if not access_token:
        raise HTTPException(status_code=401, detail="Jira not connected")

    # Layer 3: Jira Automation Preparation
    resources = get_accessible_resources(access_token)
    if not resources:
        return {"status": "no sites found"}
    cloud_id = resources[0]["id"]

    results = []
    for commit in commits:
        message = commit["message"]
        task = extract_tasks(message)
        
        if not task or task["platform"] != "jira":
            continue

        try:
            # Layer 3: Jira Action
            issue = get_issue(cloud_id, task["id"], access_token)
            decision = decide_jira_action(issue, message)

            if decision:
                add_comment(cloud_id, task["id"], decision["message"], access_token)
                
                if decision.get("action") == "transition":
                    transition_issue(cloud_id, task["id"], decision["target_status"], access_token)
                
                results.append({"task": task["id"], "action": decision.get("action")})
                        
        except Exception as e:
            print(f"Error processing {task['id']}: {e}")

    return {"status": "processed", "updates": results}
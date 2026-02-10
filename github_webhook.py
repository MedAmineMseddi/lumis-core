from fastapi import APIRouter, Request
from jira.client import get_issue
from jira.actions import add_comment
from logic.decision_engine import decide_jira_action
from token_store import get_tokens

router = APIRouter()

@router.post("/webhook/github")
async def github_webhook(request: Request):
    payload = await request.json()

    commits = payload.get("commits", [])

    for commit in commits:
        message = commit["message"]

        issue_key = extract_issue_key(message)
        if not issue_key:
            continue

        access_token = get_jira_access_token()
        issue = get_issue(issue_key, access_token)

        decision = decide_jira_action(issue, message)

        if decision and decision["action"] == "comment":
            add_comment(issue_key, decision["message"], access_token)

    return {"status": "processed"}

def decide_jira_action(issue, commit_message: str):
    status = issue["fields"]["status"]["name"]

    # Rule 1: Never touch Done issues
    if status.lower() == "done":
        return None

    # Rule 2: Always comment commits
    return {
        "action": "comment",
        "message": f"📌 Commit linked:\n{commit_message}"
    }

#to be continued with more complex rules in the future 
# or AI integration for dynamic decision making
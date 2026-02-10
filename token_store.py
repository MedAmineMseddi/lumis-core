# Replace with DB later
jira_tokens = {}

def save_tokens(user_id: str, tokens: dict):
    jira_tokens[user_id] = tokens

def get_tokens(user_id: str):
    return jira_tokens.get(user_id)

def is_connected(user_id: str) -> bool:
    return user_id in jira_tokens

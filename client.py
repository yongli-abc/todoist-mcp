"""Todoist API client — shared by MCP server and scripts."""

import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

BASE_URL = os.environ["TODOIST_API"]
TOKEN = os.environ["TODOIST_TOKEN"]

PRIORITY_LABEL = {4: "P1", 3: "P2", 2: "P3", 1: "P4"}
LABEL_PRIORITY = {"P1": 4, "P2": 3, "P3": 2, "P4": 1}

PROJECTS = {
    "Inbox": "6CrfJWMCWp8RMVGp",
    "Family": "6f36GqJqW8X7vM52",
    "Work": "6Xm3JhxW4f4qgwH5",
    "Cluster & Sailfish": "6f5MVj7hjQFGQGVr",
    "Buganizer bugs": "6XrHHqQ3hP9x9GJg",
    "Knowledge": "6Xm3P8Jvxrw3vhR4",
    "Life": "6Xm3JjHx3QV3RQmX",
    "CKA": "6cVFWpRXRxh4WppW",
    "travel": "6c6JHQj3fXwm3gxV",
    "flights": "6c72GRm4q46Hj2xf",
    "Agent": "6Xr8JfFvHFfV6Vxq",
    "LangChain AI News Feeder": "6cF8429M62XhPVcG",
    "Legal Agent": "6c6R4rq3XPCMJR7c",
    "relationship": "6XqJWwQgmc892XPQ",
    "car": "6XpCccJPc9Jh9G5f",
    "health": "6XpCc797vVwm48w2",
    "finance": "6Xm3VRppVJx4g9wF",
    "bh1204 rental": "6Xm4W49wHW375v4g",
    "pension": "6fc5gCXJc22688WX",
    "amex travel claims": "6chghfQJJ9x6Cmq9",
    "credit cards": "6cG879Mhrp6wrJv6",
    "Amex Personal Platinum": "6f5cqmCxc2vC8jhJ",
    "BA Executive Club": "6c6ChRpvG9H9vvxF",
    "sell-used": "6XpCcV3cwPWvMq3F",
    "axa claims": "6XpCW5xWGxhJQ93X",
    "cola": "6Xm3VHw8VPwQH3C9",
    "ethan": "6Xm3PvxG7QMP8fgH",
    "vaccinations": "6cJRhf5m98fvpg49",
    "education": "6Xm3V7gQF9pHq6wq",
    "Ethan Savings": "6c494JMf7hvvGfH2",
    "family": "6Xm3Pv8gGqgFf9Q2",
    "Productivity": "6Xm3VcPxXjq9HwgQ",
    "home-assistant": "6Xm4RQhcg8WfVCCj",
    "house maintenance": "6Xm3W247rrqpXG5v",
    "window films": "6Xm3W666RvWvxX7f",
    "hledger": "6Xm3Vcjr2GchJffv",
    "hledger regular imports": "6c4vCQcpwJCWF92Q",
    "CNY 2026 Trip": "6fgMRmgGPJ32wvpf",
}


def _headers():
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def get_tasks(filter: str | None = None, project_id: str | None = None) -> list[dict]:
    """Fetch all tasks, paginating through all pages."""
    params = {}
    if filter:
        params["filter"] = filter
    if project_id:
        params["project_id"] = project_id

    tasks = []
    cursor = None
    while True:
        if cursor:
            params["cursor"] = cursor
        resp = requests.get(f"{BASE_URL}/tasks", headers=_headers(), params=params)
        resp.raise_for_status()
        data = resp.json()
        tasks.extend(data.get("results", []))
        cursor = data.get("next_cursor")
        if not cursor:
            break
    return tasks


def get_task(task_id: str) -> dict:
    resp = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=_headers())
    resp.raise_for_status()
    return resp.json()


def create_task(
    content: str,
    project_id: str | None = None,
    due_string: str | None = None,
    priority: int = 1,
    description: str | None = None,
) -> dict:
    body = {"content": content, "priority": priority}
    if project_id:
        body["project_id"] = project_id
    if due_string:
        body["due_string"] = due_string
    if description:
        body["description"] = description
    resp = requests.post(f"{BASE_URL}/tasks", headers=_headers(), json=body)
    resp.raise_for_status()
    return resp.json()


def update_task(task_id: str, **fields) -> dict:
    resp = requests.post(f"{BASE_URL}/tasks/{task_id}", headers=_headers(), json=fields)
    resp.raise_for_status()
    return resp.json()


def complete_task(task_id: str) -> None:
    resp = requests.post(f"{BASE_URL}/tasks/{task_id}/close", headers=_headers())
    resp.raise_for_status()


def delete_task(task_id: str) -> None:
    resp = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=_headers())
    resp.raise_for_status()


def move_task(task_id: str, project_id: str) -> None:
    resp = requests.post(
        f"{BASE_URL}/tasks/{task_id}/move",
        headers=_headers(),
        json={"project_id": project_id},
    )
    resp.raise_for_status()


def get_projects() -> list[dict]:
    resp = requests.get(f"{BASE_URL}/projects", headers=_headers())
    resp.raise_for_status()
    return resp.json().get("results", [])


def fmt_task(t: dict) -> str:
    due = t["due"]["date"] if t.get("due") else "-"
    p = PRIORITY_LABEL.get(t["priority"], "?")
    project = t.get("project_id", "")
    return f"[{p}] {due:12} | {t['id']} | {t['content'][:70]} (project:{project})"

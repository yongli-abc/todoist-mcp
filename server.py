"""Todoist MCP server — exposes Todoist as tools to Claude."""

import json
from mcp.server.fastmcp import FastMCP
import client as todoist

mcp = FastMCP("todoist-tool")


@mcp.tool()
def list_tasks(filter: str = "", project_name: str = "") -> str:
    """List tasks. filter: Todoist filter string (e.g. 'today', 'overdue', 'p1').
    project_name: name from the known project list (optional)."""
    project_id = todoist.PROJECTS.get(project_name) if project_name else None
    tasks = todoist.get_tasks(filter=filter or None, project_id=project_id)
    if not tasks:
        return "No tasks found."
    return "\n".join(todoist.fmt_task(t) for t in tasks)


@mcp.tool()
def get_inbox() -> str:
    """List all tasks in Inbox."""
    tasks = todoist.get_tasks(project_id=todoist.PROJECTS["Inbox"])
    if not tasks:
        return "Inbox is empty."
    return f"Inbox ({len(tasks)} tasks):\n" + "\n".join(todoist.fmt_task(t) for t in tasks)


@mcp.tool()
def get_overdue() -> str:
    """List all overdue tasks."""
    tasks = todoist.get_tasks(filter="overdue")
    if not tasks:
        return "No overdue tasks."
    return f"Overdue ({len(tasks)} tasks):\n" + "\n".join(todoist.fmt_task(t) for t in tasks)


@mcp.tool()
def get_today() -> str:
    """List all tasks due today."""
    tasks = todoist.get_tasks(filter="today")
    if not tasks:
        return "No tasks due today."
    return f"Today ({len(tasks)} tasks):\n" + "\n".join(todoist.fmt_task(t) for t in tasks)


@mcp.tool()
def create_task(
    content: str,
    project_name: str = "Inbox",
    due_string: str = "",
    priority: str = "P4",
    description: str = "",
) -> str:
    """Create a new task. priority: P1/P2/P3/P4. due_string: natural language e.g. 'tomorrow', 'next Monday'."""
    project_id = todoist.PROJECTS.get(project_name, todoist.PROJECTS["Inbox"])
    p = todoist.LABEL_PRIORITY.get(priority.upper(), 1)
    task = todoist.create_task(
        content=content,
        project_id=project_id,
        due_string=due_string or None,
        priority=p,
        description=description or None,
    )
    return f"Created: {task['id']} | {task['content']}"


@mcp.tool()
def update_task(task_id: str, content: str = "", due_string: str = "", priority: str = "") -> str:
    """Update a task's content, due date, or priority."""
    fields = {}
    if content:
        fields["content"] = content
    if due_string:
        fields["due_string"] = due_string
    if priority:
        fields["priority"] = todoist.LABEL_PRIORITY.get(priority.upper(), 1)
    if not fields:
        return "Nothing to update — provide at least one of content, due_string, priority."
    todoist.update_task(task_id, **fields)
    return f"Updated task {task_id}."


@mcp.tool()
def complete_task(task_id: str) -> str:
    """Mark a task as complete."""
    todoist.complete_task(task_id)
    return f"Completed task {task_id}."


@mcp.tool()
def delete_task(task_id: str) -> str:
    """Delete a task permanently."""
    todoist.delete_task(task_id)
    return f"Deleted task {task_id}."


@mcp.tool()
def move_task(task_id: str, project_name: str) -> str:
    """Move a task to a different project by name."""
    project_id = todoist.PROJECTS.get(project_name)
    if not project_id:
        return f"Unknown project '{project_name}'. Known: {', '.join(todoist.PROJECTS.keys())}"
    todoist.move_task(task_id, project_id)
    return f"Moved task {task_id} to {project_name}."


@mcp.tool()
def list_projects() -> str:
    """List all known projects with their IDs."""
    return "\n".join(f"{name}: {pid}" for name, pid in todoist.PROJECTS.items())


if __name__ == "__main__":
    mcp.run(transport="stdio")

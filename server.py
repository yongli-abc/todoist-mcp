"""Todoist MCP server — exposes Todoist as tools to Claude."""

from datetime import date
from mcp.server.fastmcp import FastMCP
import client as todoist

mcp = FastMCP("todoist-tool")


def _resolve_project(name: str) -> str:
    """Return project ID for name — static map first, then live API lookup."""
    p = todoist.find_project(name)
    if not p:
        raise ValueError(f"Unknown project '{name}'")
    return p["id"]


def _resolve_section(name: str, project_id: str) -> str:
    """Return section ID by name within a project."""
    for s in todoist.get_sections(project_id):
        if s["name"].lower() == name.lower():
            return s["id"]
    raise ValueError(f"Unknown section '{name}' in project {project_id}")


@mcp.tool()
def list_tasks(filter: str = "", project_name: str = "") -> str:
    """List tasks. filter: Todoist filter string (e.g. 'today', 'overdue', 'p1').
    project_name: name from the known project list (optional)."""
    project_id = _resolve_project(project_name) if project_name else None
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
    today = date.today().isoformat()
    all_tasks = todoist.get_tasks()
    tasks = [
        t for t in all_tasks
        if t.get("due") and t["due"].get("date", "") < today
    ]
    if not tasks:
        return "No overdue tasks."
    return f"Overdue ({len(tasks)} tasks):\n" + "\n".join(todoist.fmt_task(t) for t in tasks)


@mcp.tool()
def get_today() -> str:
    """List all tasks due today."""
    today = date.today().isoformat()
    all_tasks = todoist.get_tasks()
    tasks = [
        t for t in all_tasks
        if t.get("due") and t["due"].get("date", "") == today
    ]
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
    parent_task_id: str = "",
    section_name: str = "",
    duration: int = 0,
    duration_unit: str = "minute",
) -> str:
    """Create a new task. priority: P1/P2/P3/P4. due_string: natural language e.g. 'tomorrow', 'next Monday'.
    parent_task_id: make this a subtask of another task. section_name: place in a section within the project.
    duration: estimated time (integer). duration_unit: 'minute' or 'day'."""
    project_id = _resolve_project(project_name)
    p = todoist.LABEL_PRIORITY.get(priority.upper(), 1)
    section_id = _resolve_section(section_name, project_id) if section_name else None
    task = todoist.create_task(
        content=content,
        project_id=project_id,
        parent_id=parent_task_id or None,
        section_id=section_id,
        due_string=due_string or None,
        priority=p,
        description=description or None,
        duration=duration or None,
        duration_unit=duration_unit,
    )
    return f"Created: {task['id']} | {task['content']}"


@mcp.tool()
def get_task(task_id: str) -> str:
    """Fetch a single task by ID, including its description and comments."""
    task = todoist.get_task(task_id)
    lines = [todoist.fmt_task(task)]
    if task.get("description"):
        lines.append(f"Description: {task['description']}")
    comments = todoist.get_comments(task_id)
    if comments:
        lines.append(f"Comments ({len(comments)}):")
        for c in comments:
            lines.append(f"  [{c.get('posted_at', '')[:10]}] {c['id']} | {c['content']}")
    return "\n".join(lines)


@mcp.tool()
def update_task(task_id: str, content: str = "", due_string: str = "", priority: str = "", description: str = "", duration: int = 0, duration_unit: str = "minute") -> str:
    """Update a task's content, due date, priority, description, or duration.
    duration: estimated time (integer). duration_unit: 'minute' or 'day'."""
    fields = {}
    if content:
        fields["content"] = content
    if due_string:
        fields["due_string"] = due_string
    if priority:
        p_key = priority.upper() if not priority.isdigit() else f"P{priority}"
        fields["priority"] = todoist.LABEL_PRIORITY.get(p_key, 1)
    if description:
        fields["description"] = description
    if duration:
        fields["duration"] = duration
        fields["duration_unit"] = duration_unit
    if not fields:
        return "Nothing to update — provide at least one of content, due_string, priority, description, duration."
    todoist.update_task(task_id, **fields)
    return f"Updated task {task_id}."


@mcp.tool()
def delete_comment(comment_id: str) -> str:
    """Delete a comment by its ID (comment IDs are shown in get_task output)."""
    todoist.delete_comment(comment_id)
    return f"Deleted comment {comment_id}."


@mcp.tool()
def add_comment(task_id: str, content: str) -> str:
    """Add a comment to a task."""
    todoist.add_comment(task_id, content)
    return f"Comment added to task {task_id}."


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
def move_task(
    task_id: str,
    project_name: str = "",
    parent_task_id: str = "",
    section_name: str = "",
) -> str:
    """Move a task to a different project, make it a subtask of another task, or move it into a section.
    Provide exactly one of: project_name, parent_task_id, or section_name."""
    if parent_task_id:
        todoist.move_task(task_id, parent_id=parent_task_id)
        return f"Moved task {task_id} under parent task {parent_task_id}."
    if project_name:
        project_id = _resolve_project(project_name)
        section_id = _resolve_section(section_name, project_id) if section_name else None
        todoist.move_task(task_id, project_id=project_id, section_id=section_id)
        dest = f"{project_name} / {section_name}" if section_name else project_name
        return f"Moved task {task_id} to {dest}."
    if section_name:
        return "Provide project_name alongside section_name so the section can be resolved."
    return "Nothing to move — provide project_name, parent_task_id, or section_name."


@mcp.tool()
def create_project(name: str, parent_project_name: str = "") -> str:
    """Create a new project, optionally as a subproject of an existing one."""
    parent_id = _resolve_project(parent_project_name) if parent_project_name else None
    project = todoist.create_project(name, parent_id=parent_id)
    location = f" under '{parent_project_name}'" if parent_project_name else ""
    return f"Created project '{project['name']}' (ID: {project['id']}){location}."


@mcp.tool()
def move_project(project_name: str, parent_project_name: str) -> str:
    """Make an existing project a subproject of another project."""
    project_id = _resolve_project(project_name)
    parent_id = _resolve_project(parent_project_name)
    todoist.update_project(project_id, parent_id=parent_id)
    return f"Moved project '{project_name}' under '{parent_project_name}'."


@mcp.tool()
def rename_project(project_name: str, new_name: str) -> str:
    """Rename an existing project."""
    project_id = _resolve_project(project_name)
    todoist.update_project(project_id, name=new_name)
    return f"Renamed project '{project_name}' to '{new_name}'."


@mcp.tool()
def delete_project(project_name: str) -> str:
    """Delete a project permanently. This cannot be undone."""
    project_id = _resolve_project(project_name)
    todoist.delete_project(project_id)
    return f"Deleted project '{project_name}'."


@mcp.tool()
def archive_project(project_name: str) -> str:
    """Archive a project (hides it without deleting tasks or history)."""
    project_id = _resolve_project(project_name)
    todoist.archive_project(project_id)
    return f"Archived project '{project_name}'."


@mcp.tool()
def delete_section(section_name: str, project_name: str) -> str:
    """Delete a section by name within a project. The section must be empty."""
    project_id = _resolve_project(project_name)
    section_id = _resolve_section(section_name, project_id)
    todoist.delete_section(section_id)
    return f"Deleted section '{section_name}' from '{project_name}'."


@mcp.tool()
def create_section(name: str, project_name: str) -> str:
    """Create a section within a project."""
    project_id = _resolve_project(project_name)
    section = todoist.create_section(name, project_id)
    return f"Created section '{section['name']}' (ID: {section['id']}) in '{project_name}'."


@mcp.tool()
def list_sections(project_name: str = "") -> str:
    """List sections, optionally filtered to a specific project."""
    project_id = _resolve_project(project_name) if project_name else None
    sections = todoist.get_sections(project_id)
    if not sections:
        return "No sections found."
    return "\n".join(f"{s['id']} | {s.get('project_id', '')} | {s['name']}" for s in sections)


@mcp.tool()
def dump_all() -> str:
    """Fetch all tasks and projects in one call for full analysis. Returns compact representation."""
    tasks = todoist.get_tasks()
    projects = todoist.get_projects()
    sections = todoist.get_sections()

    # Build project and section name lookup
    proj_map = {p["id"]: p["name"] for p in projects}
    sect_map = {s["id"]: s["name"] for s in sections}

    lines = [f"PROJECTS ({len(projects)}):"]
    for p in projects:
        parent = f" (parent: {proj_map.get(p['parent_id'], p['parent_id'])})" if p.get("parent_id") else ""
        lines.append(f"  {p['id']} | {p['name']}{parent}")

    lines.append(f"\nTASKS ({len(tasks)}):")
    for t in sorted(tasks, key=lambda t: (t.get("project_id") or "", t.get("section_id") or "")):
        due = t["due"]["date"] if t.get("due") else "-"
        p = todoist.PRIORITY_LABEL.get(t["priority"], "?")
        proj = proj_map.get(t.get("project_id", ""), "?")
        sect = f" / {sect_map[t['section_id']]}" if t.get("section_id") and t["section_id"] in sect_map else ""
        parent = f" (subtask of: {t['parent_id']})" if t.get("parent_id") else ""
        desc = f" [has description]" if t.get("description") else ""
        lines.append(f"  [{p}] {due:12} | {t['id']} | {proj}{sect} | {t['content'][:60]}{parent}{desc}")

    return "\n".join(lines)


@mcp.tool()
def get_completed(project_name: str = "", since: str = "", until: str = "", limit: int = 50) -> str:
    """List recently completed tasks. since/until: ISO date e.g. '2026-04-13'. project_name: optional filter."""
    project_id = _resolve_project(project_name) if project_name else None
    tasks = todoist.get_completed_tasks(
        project_id=project_id,
        since=since or None,
        until=until or None,
        limit=limit,
    )
    if not tasks:
        return "No completed tasks found."
    lines = [f"Completed ({len(tasks)} tasks):"]
    for t in tasks:
        completed_at = t.get("completed_at", "")[:10]
        lines.append(f"[{completed_at}] {t.get('id', '')} | {t.get('content', '')[:70]}")
    return "\n".join(lines)


@mcp.tool()
def list_projects() -> str:
    """List all projects (static known projects + any created dynamically)."""
    projects = todoist.get_projects()
    if not projects:
        return "No projects found."
    return "\n".join(f"{p['id']} | {p['name']}" + (f" (parent: {p['parent_id']})" if p.get("parent_id") else "") for p in projects)


if __name__ == "__main__":
    mcp.run(transport="stdio")

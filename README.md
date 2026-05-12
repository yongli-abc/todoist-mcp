# todoist-mcp

A [Model Context Protocol](https://modelcontextprotocol.io/) server that exposes your Todoist as tools to Claude. Manage tasks, projects, and sections through natural language in Claude Code or any MCP-compatible client.

## Features

**Tasks**
- List tasks with Todoist filter strings (`today`, `overdue`, `p1 & !assigned to: others`, etc.)
- Get inbox, today's tasks, or overdue tasks
- Create tasks with priority, due date, description, subtasks, and sections
- Update, complete, delete, or move tasks
- Add and delete comments
- Fetch completed task history

**Projects**
- List, create, rename, archive, delete projects
- Nest projects under parent projects

**Sections**
- List, create, delete sections within projects

**Bulk**
- `dump_all` — fetch every task, project, and section in one call for full analysis

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Todoist account with an [API token](https://app.todoist.com/app/settings/integrations/developer)

## Setup

### 1. Clone and install

```bash
git clone https://github.com/neilli1992/todoist-mcp
cd todoist-mcp
uv sync
```

### 2. Configure credentials

Create a `.env` file (gitignored):

```
TODOIST_TOKEN=your_api_token_here
TODOIST_API=https://api.todoist.com/api/v1
```

### 3. Configure your project map

`client.py` contains a `PROJECTS` dict mapping human-readable names to Todoist project IDs. Update it with your own projects — the server uses these for name-to-ID resolution so you can refer to projects by name instead of ID.

Get your project IDs from the Todoist API:

```bash
curl -s https://api.todoist.com/api/v1/projects \
  -H "Authorization: Bearer YOUR_TOKEN" | python3 -m json.tool | grep -E '"id"|"name"'
```

### 4. Register with Claude Code

Add to `~/.claude/settings.json` under `mcpServers`:

```json
{
  "mcpServers": {
    "todoist": {
      "command": "uv",
      "args": ["run", "mcp", "run", "server.py"],
      "cwd": "/path/to/todoist-mcp"
    }
  }
}
```

Restart Claude Code. The `mcp__todoist__*` tools will appear automatically.

## Usage

Once registered, just talk to Claude:

```
What's in my inbox?
Create a task "Book dentist" in the health project, due next week, P2
Move the dentist task to the family project
Show me everything overdue
Dump all my tasks so we can do a weekly review
```

## Scripts

`scripts/review.py` — daily review: prints overdue + today + inbox  
`scripts/triage.py` — inbox triage with routing hints

```bash
uv run python scripts/review.py
uv run python scripts/triage.py
```

## Priority mapping

Todoist's internal priority is inverted from the UI label:

| UI label | API value |
|----------|-----------|
| P1       | 4         |
| P2       | 3         |
| P3       | 2         |
| P4       | 1         |

The server accepts `P1`/`P2`/`P3`/`P4` strings and converts automatically.

## Project structure

```
server.py    — MCP server (FastMCP), all tool definitions
client.py    — Todoist REST API client, shared by server and scripts
scripts/     — standalone CLI scripts
```

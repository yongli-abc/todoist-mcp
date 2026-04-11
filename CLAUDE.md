# todoist-tool

MCP server + scripts for managing Yong's Todoist.

## Structure

- `client.py` — shared Todoist API client (handles pagination, all CRUD)
- `server.py` — MCP server (run via `mcp` CLI, registered in ~/.claude/settings.json)
- `scripts/review.py` — daily review: overdue + today + inbox
- `scripts/triage.py` — inbox triage with routing hints
- `.env` — API token (gitignored)

## MCP Setup

The server is registered in `~/.claude/settings.json` under `mcpServers`.
Run manually with: `uv run mcp run server.py`

## API

- Base: `https://api.todoist.com/api/v1`
- Token in `.env` as `TODOIST_TOKEN`
- Priority: `4`=P1, `3`=P2, `2`=P3, `1`=P4 (inverted from UI)
- Always paginate via `next_cursor` — 100+ tasks across pages

## Project Map

| Name | ID |
|------|----|
| Inbox | 6CrfJWMCWp8RMVGp |
| 👨‍👩‍👦 Family | 6f36GqJqW8X7vM52 |
| 👾 Work | 6Xm3JhxW4f4qgwH5 |
| 💠 Cluster & Sailfish | 6f5MVj7hjQFGQGVr |
| 🪲 Buganizer bugs | 6XrHHqQ3hP9x9GJg |
| 💡 Knowledge | 6Xm3P8Jvxrw3vhR4 |
| Life | 6Xm3JjHx3QV3RQmX |
| 🔰 CKA | 6cVFWpRXRxh4WppW |
| 🏖️ travel | 6c6JHQj3fXwm3gxV |
| 🛫 flights | 6c72GRm4q46Hj2xf |
| 🤖 Agent | 6Xr8JfFvHFfV6Vxq |
| 🗞️ LangChain AI News Feeder | 6cF8429M62XhPVcG |
| ⚖️ Legal Agent | 6c6R4rq3XPCMJR7c |
| 🤝 relationship | 6XqJWwQgmc892XPQ |
| 🚐 car | 6XpCccJPc9Jh9G5f |
| 💪 health | 6XpCc797vVwm48w2 |
| 💰 finance | 6Xm3VRppVJx4g9wF |
| 🏦 bh1204 rental | 6Xm4W49wHW375v4g |
| 🧓🏻 pension | 6fc5gCXJc22688WX |
| 🏥 amex travel claims | 6chghfQJJ9x6Cmq9 |
| 💳 credit cards | 6cG879Mhrp6wrJv6 |
| Amex Personal Platinum | 6f5cqmCxc2vC8jhJ |
| ✈️ BA Executive Club | 6c6ChRpvG9H9vvxF |
| 💰 sell-used | 6XpCcV3cwPWvMq3F |
| ❤️‍🩹 axa claims | 6XpCW5xWGxhJQ93X |
| 🐶 cola | 6Xm3VHw8VPwQH3C9 |
| 👶 ethan | 6Xm3PvxG7QMP8fgH |
| 💉 vaccinations | 6cJRhf5m98fvpg49 |
| 📚 education | 6Xm3V7gQF9pHq6wq |
| 🐣 Ethan Savings | 6c494JMf7hvvGfH2 |
| 👨‍👩‍👦 family | 6Xm3Pv8gGqgFf9Q2 |
| ☯️ Productivity | 6Xm3VcPxXjq9HwgQ |
| home-assistant | 6Xm4RQhcg8WfVCCj |
| 🏡 house maintenance | 6Xm3W247rrqpXG5v |
| window films | 6Xm3W666RvWvxX7f |
| 💰 hledger | 6Xm3Vcjr2GchJffv |
| ⏰ hledger regular imports | 6c4vCQcpwJCWF92Q |
| CNY 2026 Trip | 6fgMRmgGPJ32wvpf |

## My Responsibilities

1. **Daily review**: Highlight overdue tasks and tasks due today/this week — always include Inbox
2. **Inbox triage**: Always check Inbox as part of any review — Yong forgets to triage it
3. **Task hygiene**: Flag stale tasks, duplicate tasks, tasks without due dates on time-sensitive items
4. **Prioritisation help**: Suggest priority/due date when asked
5. **Smart routing**: Know which project a new task belongs to without asking
6. **Pattern learning**: Track recurring tasks and suggest automation over time

## Context About Yong

- Works at Google on Cluster & Sailfish / TPU Slice infrastructure (uses Buganizer for bug tracking)
- Based in the UK
- Son named Ethan (young child — vaccination schedule tracked in `vaccinations` project)
- Dog named Cola
- Owns rental property bh1204
- Tracks finances with hledger
- Holds Amex Personal Platinum and BA Executive Club memberships
- Interested in AI agents, Kubernetes (studying for CKA), LangChain
- Tasks sometimes written in Chinese

## Improvement Log

- (2026-04-07) Initial setup in todoist-agent. 50 active tasks across 37 projects.
- (2026-04-07) Time-sensitive: Cola medication (Advocate Apr 8, Droncit Apr 30), bh1204 deposit return (overdue Apr 3), BA Avios booster (Apr 22).
- (2026-04-07) Recurring finance tasks: hledger imports (Marcus, WeChat), pension contributions, Amex Platinum dining credits.
- (2026-04-07) Ethan vaccination schedule tracked — likely needs due dates added.
- (2026-04-11) Migrated from todoist-agent to todoist-tool. Added MCP server + Python client layer.

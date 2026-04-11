#!/usr/bin/env python3
"""Daily review: overdue tasks + today's tasks + inbox count."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import client as todoist


def main():
    overdue = todoist.get_tasks(filter="overdue")
    today = todoist.get_tasks(filter="today")
    inbox = todoist.get_tasks(project_id=todoist.PROJECTS["Inbox"])

    print(f"=== Daily Review ===\n")

    print(f"OVERDUE ({len(overdue)}):")
    if overdue:
        for t in sorted(overdue, key=lambda t: (t.get("due", {}) or {}).get("date", "")):
            print(f"  {todoist.fmt_task(t)}")
    else:
        print("  None")

    print(f"\nTODAY ({len(today)}):")
    if today:
        for t in sorted(today, key=lambda t: t["priority"], reverse=True):
            print(f"  {todoist.fmt_task(t)}")
    else:
        print("  None")

    print(f"\nINBOX ({len(inbox)}):")
    if inbox:
        for t in inbox:
            print(f"  {todoist.fmt_task(t)}")
    else:
        print("  Empty")


if __name__ == "__main__":
    main()

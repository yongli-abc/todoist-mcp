#!/usr/bin/env python3
"""Inbox triage: list inbox tasks with suggested project routing."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import client as todoist

# Keywords → suggested project (rough heuristics, Claude can do the real routing)
ROUTING_HINTS = {
    ("buganizer", "b/", "cluster", "sailfish", "tpu", "borg", "google"): "Work",
    ("ethan", "school", "vaccination", "nursery"): "ethan",
    ("cola", "vet", "flea", "worm"): "cola",
    ("amex", "avios", "ba ", "flight", "travel"): "finance",
    ("hledger", "import", "marcus", "pension"): "finance",
    ("bh1204", "tenant", "deposit", "landlord"): "bh1204 rental",
    ("cka", "kubernetes", "k8s"): "CKA",
}


def suggest_project(content: str) -> str:
    lower = content.lower()
    for keywords, project in ROUTING_HINTS.items():
        if any(kw in lower for kw in keywords):
            return project
    return "?"


def main():
    inbox = todoist.get_tasks(project_id=todoist.PROJECTS["Inbox"])
    if not inbox:
        print("Inbox is empty.")
        return

    print(f"=== Inbox Triage ({len(inbox)} tasks) ===\n")
    for t in inbox:
        suggestion = suggest_project(t["content"])
        due = t["due"]["date"] if t.get("due") else "no date"
        p = todoist.PRIORITY_LABEL.get(t["priority"], "?")
        print(f"  [{p}] {t['id']} | {t['content'][:60]}")
        print(f"         due:{due}  → suggest: {suggestion}\n")


if __name__ == "__main__":
    main()

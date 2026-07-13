#!/usr/bin/env python3
"""
generate_and_commit.py

Pops the next pending item from topics/queue.yaml, asks the Claude API to draft
the file, writes it, updates the README index, then commits and pushes.

Environment:
  ANTHROPIC_API_KEY   required (set as a GitHub Actions secret in production)

Run locally:
  ANTHROPIC_API_KEY=sk-... python scripts/generate_and_commit.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml
from anthropic import Anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = REPO_ROOT / "topics" / "queue.yaml"
README_PATH = REPO_ROOT / "README.md"

INDEX_START = "<!-- AUTO-GENERATED-INDEX-START -->"
INDEX_END = "<!-- AUTO-GENERATED-INDEX-END -->"


def load_queue() -> list[dict]:
    with open(QUEUE_PATH) as f:
        return yaml.safe_load(f) or []


def save_queue(items: list[dict]) -> None:
    with open(QUEUE_PATH, "w") as f:
        yaml.safe_dump(items, f, sort_keys=False)


def next_pending(items: list[dict]) -> dict | None:
    return next((item for item in items if item.get("status") == "pending"), None)


def generate_code(item: dict) -> str:
    """Ask Claude to draft the file. Swap the model string for whatever's current
    at docs.claude.com/en/docs/about-claude/models."""
    client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    prompt = (
        f"Write a single, complete, working {item['language']} file.\n"
        f"Title: {item['title']}\n"
        f"Requirements: {item['brief']}\n\n"
        "Rules:\n"
        "- Roughly 15-80 lines of actual code (comments don't count against this).\n"
        "- Idiomatic, production-quality code — no placeholders or TODOs.\n"
        "- A short file-level comment explaining what it does.\n"
        "- Brief inline comments only where the logic isn't obvious.\n"
        "- Output ONLY the file content. No prose, no markdown fences."
    )
    resp = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(block.text for block in resp.content if block.type == "text").strip()
    text = re.sub(r"^```[\w+-]*\n", "", text)  # defensive: strip an accidental code fence
    text = re.sub(r"\n```$", "", text)
    return text.strip() + "\n"


def update_readme_index(item: dict) -> None:
    readme = README_PATH.read_text()
    entry = f"- [{item['title']}]({item['path']}) — {item['brief']}"
    pattern = re.compile(re.escape(INDEX_START) + r"(.*?)" + re.escape(INDEX_END), re.DOTALL)
    match = pattern.search(readme)
    if not match:
        raise RuntimeError("README index markers not found — did someone edit them?")

    existing = match.group(1).strip()
    if existing.startswith("_(entries appear"):
        existing = ""
    body = f"{existing}\n{entry}" if existing else entry
    README_PATH.write_text(pattern.sub(f"{INDEX_START}\n{body}\n{INDEX_END}", readme))


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def commit_and_push(item: dict) -> tuple[str, str]:
    run(["git", "add", item["path"], "topics/queue.yaml", "README.md"])
    message = f"Add {item['title']}"
    run(["git", "commit", "-m", message])
    run(["git", "push"])
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip(), message


def main() -> None:
    items = load_queue()
    item = next_pending(items)
    if item is None:
        print("No pending items in topics/queue.yaml — add more before the next run.")
        sys.exit(0)

    file_path = REPO_ROOT / item["path"]
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(generate_code(item))

    update_readme_index(item)
    item["status"] = "done"
    save_queue(items)

    commit_hash, message = commit_and_push(item)
    print(f"filename: {item['path']}")
    print(f"commit_message: {message}")
    print(f"commit_hash: {commit_hash}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Tanjun Issue Bot — Automated issue-to-PR pipeline.

Runs as a cron job. Each run:
1. Picks the oldest open issue in milestone "1.2" (unassigned to this bot)
2. Reads its full body and context
3. Creates a feature branch from development
4. Uses an AI agent (OpenRouter via configured env) to implement the fix
5. Pushes branch, creates PR to development
6. Requests @coderabbitai review
7. Waits for CodeRabbit to finish, fixes issues, repeats
8. Merges PR, closes issue

Usage:
    python .github/scripts/tanjun_issue_bot.py
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# ─── Configuration ───────────────────────────────────────────────────────────

REPO = "TanjunBot/new_tanjun"
BASE_BRANCH = "development"
MILESTONE_TITLE = "1.2"
POLL_INTERVAL_SECONDS = 60  # How long between CodeRabbit status checks
MAX_REVIEW_CYCLES = 15  # Safety: max review-fix loops before aborting
BOT_LABEL = "tanjun-issue-bot"  # Label we'll apply to issues we're working on

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3-0324:free")

WORKSPACE = Path(__file__).resolve().parent.parent.parent
REPO_DIR = WORKSPACE

# ─── Helpers ─────────────────────────────────────────────────────────────────


def run(cmd: list[str], cwd: str | None = None, timeout: int = 120, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or str(REPO_DIR), timeout=timeout, check=check)


def gh(args: list[str], input_data: str | None = None) -> Any:
    """Run `gh` command and parse JSON output."""
    cmd = ["gh"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_DIR), timeout=60, input=input_data)
    if result.returncode != 0:
        print(f"gh error: {result.stderr}")
        result.check_returncode()
    if result.stdout.strip():
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return result.stdout.strip()
    return None


def log(msg: str):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def ai_complete(prompt: str, system_prompt: str | None = None) -> str:
    """Call OpenRouter to get a code implementation."""
    if not OPENROUTER_API_KEY:
        log("ERROR: OPENROUTER_API_KEY not set")
        sys.exit(1)

    import requests

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 16000,
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


# ─── Issue Selection ─────────────────────────────────────────────────────────


def get_next_issue() -> dict | None:
    """Find the oldest open issue in the target milestone, not already being worked on."""
    issues = gh(
        [
            "issue",
            "list",
            "--repo",
            REPO,
            "--milestone",
            MILESTONE_TITLE,
            "--state",
            "open",
            "--json",
            "number,title,body,labels,created_at",
            "-L",
            "50",
        ]
    )
    if not issues:
        return None

    # Filter out issues already labeled with BOT_LABEL
    candidates = []
    for iss in issues:
        label_names = [l["name"] for l in iss.get("labels", [])]
        if BOT_LABEL not in label_names:
            candidates.append(iss)

    if not candidates:
        return None

    # Pick oldest (first created)
    candidates.sort(key=lambda x: x["created_at"])
    return candidates[0]


# ─── Branch & Implementation ────────────────────────────────────────────────


def create_branch(issue: dict) -> str:
    """Create a feature branch for the issue."""
    number = issue["number"]
    title = issue["title"]
    # Sanitize title for branch name
    safe_title = re.sub(r"[^a-zA-Z0-9-_\s]", "", title).strip().lower()
    safe_title = re.sub(r"\s+", "-", safe_title)[:60]
    safe_title = re.sub(r"-+$", "", safe_title)
    branch = f"fix/issue-{number}-{safe_title}"

    run(["git", "checkout", BASE_BRANCH])
    run(["git", "pull", "origin", BASE_BRANCH])
    run(["git", "checkout", "-b", branch])

    return branch


def implement_issue(issue: dict, branch: str) -> bool:
    """Use AI to understand the issue and write the code changes."""
    number = issue["number"]
    title = issue["title"]
    body = issue.get("body", "") or ""

    log(f"Implementing issue #{number}: {title}")

    # Read some context about the repo structure
    repo_structure = subprocess.run(
        ["find", ".", "-type", "f", "-name", "*.py", "! -path './.git/*'", "! -path './.venv/*'", "! -path './__pycache__/*'"],
        capture_output=True,
        text=True,
        cwd=str(REPO_DIR),
        timeout=30,
    ).stdout.strip()[:5000]

    # Read key files for context
    main_py = Path(REPO_DIR / "main.py").read_text()[:2000] if (REPO_DIR / "main.py").exists() else ""
    config_py = Path(REPO_DIR / "config.py").read_text()[:2000] if (REPO_DIR / "config.py").exists() else ""

    system_prompt = """You are an expert Python developer working on Tanjun, a Discord bot.
Your task is to implement the exact changes described in the issue below.
- Write clean, maintainable code that fits the existing codebase style.
- Do NOT make changes outside the scope of the issue.
- Output ONLY a JSON array of file changes in this exact format:
[
  {
    "path": "relative/file/path.py",
    "content": "full file content here (or the changes if it's a new file)",
    "action": "modify" | "create" | "delete"
  }
]
- For "modify", provide the FULL new file content, not just a diff.
- Make sure to write production-quality code.
"""

    prompt = f"""
Issue #{number}: {title}

Body:
{body}

Repository structure (Python files):
{repo_structure}

Key files:
- main.py (first 2000 chars): {main_py}
- config.py (first 2000 chars): {config_py}

Implement the changes needed to resolve this issue. Only change what's necessary.
Output a JSON array of file changes following the format specified.
"""

    result = ai_complete(prompt, system_prompt)

    # Parse JSON from response (handle markdown code fences)
    json_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", result, re.DOTALL)
    if json_match:
        result = json_match.group(1)

    result = result.strip()
    # Remove leading/trailing non-JSON noise
    if result.startswith("["):
        # Good
        pass
    elif "[" in result and "]" in result:
        result = result[result.index("[") : result.rindex("]") + 1]
    else:
        log(f"AI response wasn't valid JSON. Full response:\n{result[:2000]}")
        return False

    try:
        changes = json.loads(result)
    except json.JSONDecodeError as e:
        log(f"Failed to parse AI output as JSON: {e}")
        log(f"Raw output (first 2000): {result[:2000]}")
        return False

    for change in changes:
        path = Path(REPO_DIR / change["path"])
        action = change.get("action", "modify")

        if action == "delete":
            if path.exists():
                path.unlink()
                run(["git", "rm", change["path"]])
                log(f"Deleted {change['path']}")
            continue

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        if action == "create" and path.exists():
            log(f"File {change['path']} already exists, skipping creation")
            continue

        path.write_text(change["content"])
        log(f"{'Created' if action == 'create' else 'Modified'} {change['path']}")

    return True


# ─── PR Creation ────────────────────────────────────────────────────────────


def create_pr(issue: dict, branch: str) -> int:
    """Push branch and create PR. Returns PR number."""
    run(["git", "add", "-A"])
    diff_stat = run(["git", "diff", "--stat", "--cached"], check=False).stdout.strip()
    run(
        [
            "git",
            "commit",
            "-m",
            f"fix(#{issue['number']}): {issue['title']}\n\nAutomated fix by tanjun-issue-bot.\n\n{diff_stat}",
        ]
    )
    run(["git", "push", "origin", branch, "-u"])

    body = f"""## Automated Fix for Issue #{issue["number"]}

**Issue:** {issue["title"]}

This PR was automatically generated by the Tanjun Issue Bot.

Closes #{issue["number"]}

> _Please review by the CodeRabbit AI. If further changes are needed, the bot will address them._
"""
    pr_data = gh(
        [
            "pr",
            "create",
            "--repo",
            REPO,
            "--base",
            BASE_BRANCH,
            "--head",
            branch,
            "--title",
            f"fix(#{issue['number']}): {issue['title']}",
            "--body",
            body,
            "--label",
            BOT_LABEL,
        ]
    )

    if isinstance(pr_data, dict):
        return pr_data["number"]
    elif isinstance(pr_data, str):
        # Parse URL
        match = re.search(r"/(\d+)$", pr_data)
        if match:
            return int(match.group(1))
    return 0


# ─── CodeRabbit Review Loop ──────────────────────────────────────────────


def request_coderabbit_review(pr_number: int):
    """Comment on the PR to request CodeRabbit review."""
    log(f"Requesting CodeRabbit review on PR #{pr_number}")
    gh(["pr", "comment", "--repo", REPO, str(pr_number), "--body", "@coderabbitai review"])


def get_coderabbit_review_state(pr_number: int) -> str | None:
    """Check CodeRabbit's review state on the PR. Returns status or None."""
    reviews = gh(
        [
            "pr",
            "view",
            str(pr_number),
            "--repo",
            REPO,
            "--json",
            "reviews",
        ]
    )
    if not reviews:
        return None

    for rev in reviews.get("reviews", []):
        author = rev.get("author", {}).get("login", "")
        if "coderabbit" in author.lower() or "coderabbitai" in author.lower():
            state = rev.get("state", "")
            if state in ("APPROVED", "CHANGES_REQUESTED", "COMMENTED"):
                return state
    return None


def get_coderabbit_review_body(pr_number: int) -> str:
    """Get the latest review body from CodeRabbit."""
    reviews = gh(
        [
            "pr",
            "view",
            str(pr_number),
            "--repo",
            REPO,
            "--json",
            "reviews",
        ]
    )
    if not reviews:
        return ""
    for rev in reversed(reviews.get("reviews", [])):
        author = rev.get("author", {}).get("login", "")
        if "coderabbit" in author.lower() or "coderabbitai" in author.lower():
            body = rev.get("body", "")
            if body:
                return body
    return ""


def fix_review_issues(pr_number: int, branch: str, review_body: str) -> bool:
    """Use AI to fix issues CodeRabbit pointed out."""
    log("Fixing issues pointed out by CodeRabbit...")

    # Get current state of changed files
    pr_diff = gh(
        [
            "pr",
            "diff",
            str(pr_number),
            "--repo",
            REPO,
        ]
    )
    pr_diff = str(pr_diff) if pr_diff else ""

    system_prompt = """You are an expert Python developer fixing issues identified by a code review.
Output ONLY a JSON array of file changes in this format:
[
  {
    "path": "relative/file/path.py",
    "content": "full file content with fixes applied",
    "action": "modify" | "create"
  }
]
For "modify", provide the FULL new file content.
Address ALL review comments — do not leave any unresolved.
"""

    prompt = f"""
PR #{pr_number} has been reviewed by CodeRabbit AI.

Review comments:
{review_body}

Current diff of the PR:
{pr_diff}

Fix all the issues identified by the CodeRabbit review. Apply minimal, targeted fixes.
Output a JSON array of file changes.
"""

    result = ai_complete(prompt, system_prompt)

    # Parse JSON
    json_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", result, re.DOTALL)
    if json_match:
        result = json_match.group(1)
    result = result.strip()
    if "[" in result and "]" in result:
        result = result[result.index("[") : result.rindex("]") + 1]

    try:
        changes = json.loads(result)
    except json.JSONDecodeError as e:
        log(f"Failed to parse fix response as JSON: {e}")
        log(f"Raw: {result[:2000]}")
        return False

    for change in changes:
        path = Path(REPO_DIR / change["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(change["content"])
        log(f"Fixed {change['path']}")

    # Commit and push fixes
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", f"fix(pr #{pr_number}): Address CodeRabbit review feedback"])
    run(["git", "push", "origin", branch])
    return True


def wait_for_coderabbit(pr_number: int, branch: str) -> bool:
    """
    Wait for CodeRabbit and handle review feedback.
    Returns True if PR is approved, False if we gave up.
    """
    for cycle in range(1, MAX_REVIEW_CYCLES + 1):
        log(f"Review cycle {cycle}/{MAX_REVIEW_CYCLES} — waiting {POLL_INTERVAL_SECONDS}s for CodeRabbit...")
        time.sleep(POLL_INTERVAL_SECONDS)

        state = get_coderabbit_review_state(pr_number)
        log(f"CodeRabbit review state: {state}")

        if state == "APPROVED":
            log("CodeRabbit approved!")
            return True
        elif state == "CHANGES_REQUESTED":
            log("CodeRabbit requested changes. Fixing...")
            review_body = get_coderabbit_review_body(pr_number)
            if not fix_review_issues(pr_number, branch, review_body):
                log("Failed to fix review issues, retrying...")
            # After fix, re-request review
            gh(["pr", "comment", "--repo", REPO, str(pr_number), "--body", "@coderabbitai review"])
            continue
        elif state == "COMMENTED":
            # Might still have issues in comments
            log("CodeRabbit commented. Checking for requested changes...")
            review_body = get_coderabbit_review_body(pr_number)
            if "change" in review_body.lower() or "fix" in review_body.lower() or "issue" in review_body.lower():
                fix_review_issues(pr_number, branch, review_body)
                gh(["pr", "comment", "--repo", REPO, str(pr_number), "--body", "@coderabbitai review"])
            else:
                log("No changes requested in comment. Proceeding...")
                return True
        else:
            log("No CodeRabbit review yet or pending...")

    log(f"MAX_REVIEW_CYCLES ({MAX_REVIEW_CYCLES}) reached. Aborting.")
    return False


# ─── Merge & Close ───────────────────────────────────────────────────────


def merge_and_close(pr_number: int, issue_number: int) -> bool:
    """Merge PR into development and close the issue."""
    log(f"Merging PR #{pr_number} into {BASE_BRANCH}...")

    # Check mergeability first
    pr_data = gh(["pr", "view", str(pr_number), "--repo", REPO, "--json", "mergeable,reviews,state"])
    if pr_data:
        log(f"PR state: {pr_data}")

    # Squash merge
    try:
        gh(["pr", "merge", str(pr_number), "--repo", REPO, "--squash", "--delete-branch"])
        log(f"PR #{pr_number} merged successfully!")
    except Exception as e:
        log(f"Merge failed: {e}")
        return False

    # Close the issue
    try:
        gh(
            [
                "issue",
                "close",
                str(issue_number),
                "--repo",
                REPO,
                "--comment",
                f"Fixed in PR #{pr_number} and merged into {BASE_BRANCH}.",
            ]
        )
        log(f"Issue #{issue_number} closed!")
    except Exception as e:
        log(f"Failed to close issue: {e}")

    return True


# ─── Main ─────────────────────────────────────────────────────────────────


def main():
    log("Tanjun Issue Bot starting...")

    # Ensure we're on the right branch and up-to-date
    run(["git", "checkout", BASE_BRANCH])
    run(["git", "pull", "origin", BASE_BRANCH])

    # Find next issue
    issue = get_next_issue()
    if not issue:
        log("No unassigned issues found in milestone 1.2. Nothing to do.")
        return

    number = issue["number"]
    title = issue["title"]
    log(f"Selected issue #{number}: {title}")

    # Label it so we don't pick it again
    gh(["issue", "edit", str(number), "--repo", REPO, "--add-label", BOT_LABEL])
    log(f"Labeled issue #{number} with {BOT_LABEL}")

    try:
        # Create branch
        branch = create_branch(issue)
        log(f"Created branch: {branch}")

        # Implement the fix
        if not implement_issue(issue, branch):
            log("Failed to implement issue. Cleaning up.")
            run(["git", "checkout", BASE_BRANCH], check=False)
            run(["git", "branch", "-D", branch], check=False)
            gh(["issue", "edit", str(number), "--repo", REPO, "--remove-label", BOT_LABEL])
            return

        # Create PR
        pr_number = create_pr(issue, branch)
        if not pr_number:
            log("Failed to create PR.")
            return
        log(f"Created PR #{pr_number}")

        # Go back to development for the working directory
        run(["git", "checkout", BASE_BRANCH])

        # Request CodeRabbit review
        request_coderabbit_review(pr_number)

        # Wait for and handle review
        if wait_for_coderabbit(pr_number, branch):
            log("CodeRabbit is happy! Merging...")
            # Re-checkout branch to merge
            run(["git", "checkout", branch], check=False)
            run(["git", "pull", "origin", branch], check=False)
            merge_and_close(pr_number, number)
        else:
            log("Could not get CodeRabbit approval. PR left open for manual review.")

    except Exception as e:
        log(f"ERROR: {e}")
        raise

    log("Done!")


if __name__ == "__main__":
    main()

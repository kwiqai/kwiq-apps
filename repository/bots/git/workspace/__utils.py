import subprocess
import sys


def run_git_command(command):
    try:
        result = subprocess.run(["git"] + command, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        sys.exit(1)


def check_for_uncommitted_changes():
    status = run_git_command(["status", "--porcelain"])
    return len(status.strip()) > 0


def commit_changes(commit_message):
    run_git_command(["add", "."])
    run_git_command(["commit", "-m", commit_message])


def push_changes(branch_name):
    run_git_command(["push", "origin", branch_name])


def is_remote_ahead(branch_name):
    run_git_command(["fetch", "origin", branch_name])
    status = run_git_command(["log", "HEAD..origin/" + branch_name, "--oneline"])
    return len(status.strip()) > 0


def list_recent_branches():
    branches_info = run_git_command(
        ["for-each-ref", "--sort=-committerdate", "--format=%(committerdate:short) %(authorname) %(refname:short)",
         "refs/heads"])
    recent_branches = branches_info.strip().split("\n")[:6]
    return recent_branches


def switch_to_branch(branch_name):
    run_git_command(["checkout", branch_name])

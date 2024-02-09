import __utils


def push_workspace():
    recent_branches = __utils.list_recent_branches()
    print("Available branches for merging:")
    for branch in recent_branches:
        print(branch)

    target_branch = input("Select a target branch for merging: ")
    workspace_branch = "shailendra_ws"

    __utils.run_git_command(["checkout", target_branch])
    __utils.run_git_command(["merge", workspace_branch])
    __utils.run_git_command(["branch", "-d", workspace_branch])
    print(f"Workspace changes have been merged into '{target_branch}' and workspace branch deleted.")

import sys

import __utils


def handle_uncommitted_changes():
    print("Uncommitted changes detected.")
    choice = input("Choose action: [c]ommit, [d]iscard changes, [a]bort: ").lower()

    if choice == 'c':
        commit_message = input("Enter commit message: ")
        __utils.commit_changes(commit_message)
        print("Changes committed.")
    elif choice == 'd':
        __utils.run_git_command(["reset", "--hard"])
        print("Local changes discarded.")
    elif choice == 'a':
        print("Operation aborted.")
        sys.exit(0)
    else:
        print("Invalid choice. Operation aborted.")
        sys.exit(1)


def create_workspace(workspace_branch):
    recent_branches = __utils.list_recent_branches()
    print("Recent branches:")
    for branch in recent_branches:
        print(branch)

    selected_branch = input("Select a base branch for your workspace: ")

    if workspace_branch in recent_branches:
        print(f"Workspace branch '{workspace_branch}' already exists.")
        return

    # Check for uncommitted local changes
    if __utils.check_for_uncommitted_changes():
        # print("Warning: Uncommitted local changes detected. Please commit or stash your changes before proceeding.")
        handle_uncommitted_changes()
        # return

    # Switch to the selected base branch if it's not the current branch
    current_branch = __utils.run_git_command(["rev-parse", "--abbrev-ref", "HEAD"]).strip()
    if selected_branch != current_branch:
        print(f"Switching to branch '{selected_branch}' to create the workspace branch.")
        __utils.switch_to_branch(selected_branch)

    # Check for remote changes in the base branch
    if __utils.is_remote_ahead(selected_branch):
        print(f"Newer changes available in the remote repository for branch '{selected_branch}'.")
        print("Pulling latest changes...")
        __utils.pull_changes(selected_branch)

    # Create the new workspace branch from the selected base branch
    __utils.run_git_command(["checkout", "-b", workspace_branch, selected_branch])
    print(f"Workspace branch '{workspace_branch}' created from '{selected_branch}'.")


def main():
    commit_message = "Auto-sync changes"
    workspace_branch = "shailendra_ws"

    create_workspace(workspace_branch)


if __name__ == "__main__":
    main()

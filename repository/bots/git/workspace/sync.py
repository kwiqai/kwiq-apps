import subprocess
import sys

import __utils


def sync_workspace(branch_name, commit_message):
    if __utils.is_remote_ahead(branch_name):
        print("Newer changes available in the remote repository.")
        # Check for uncommitted local changes
        if __utils.check_for_uncommitted_changes():
            print("Warning: Uncommitted local changes detected.")
            choice = input("Choose action: [m]erge, [d]iscard local changes, [o]verwrite remote changes: ").lower()

            if choice == 'm':
                # Merge changes
                try:
                    __utils.run_git_command(["stash"])
                    __utils.run_git_command(["pull", "origin", branch_name])
                    __utils.run_git_command(["stash", "pop"])
                    print("Local changes have been merged with remote changes.")
                except subprocess.CalledProcessError as e:
                    print(f"Merge failed: {e.stderr}")
                    sys.exit(1)

            elif choice == 'd':
                # Discard local changes
                __utils.run_git_command(["reset", "--hard"])
                __utils.run_git_command(["pull", "origin", branch_name])
                print("Local changes have been discarded and remote changes pulled.")

            elif choice == 'o':
                # Overwrite remote changes with local changes
                __utils.run_git_command(["push", "-f", "origin", branch_name])
                print("Remote branch has been overwritten with local changes.")
            else:
                print("Invalid choice. Operation cancelled.")
                sys.exit(1)
        else:
            # No uncommitted changes, just pull the latest changes
            __utils.run_git_command(["pull", "origin", branch_name])
    else:
        if __utils.check_for_uncommitted_changes():
            print("Uncommitted changes detected. Committing and pushing to remote branch.")
            __utils.commit_changes(commit_message)
            __utils.push_changes(branch_name)
        else:
            print("No uncommitted changes. Pulling latest updates from remote branch.")


def main():
    commit_message = "Auto-sync changes"
    branch_name = "shailendra_ws"

    sync_workspace(branch_name, commit_message)


if __name__ == "__main__":
    main()

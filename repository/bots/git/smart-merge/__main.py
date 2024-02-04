from git import Repo
import difflib
import os

from commons import RepoInfo


# upstream diff are between base and target branches
def generate_upstream_diffs(repo_path, base_branch, target_branch):
    repo = Repo(repo_path)
    base_commit = repo.commit(base_branch)
    target_commit = repo.commit(target_branch)
    diffs = base_commit.diff(target_commit, create_patch=True)
    return diffs


def split_diffs(diffs, patches_dir):
    for diff_item in diffs:
        # Determine the appropriate file path (handle renames, additions, deletions)
        if diff_item.deleted_file:
            file_path = diff_item.a_path  # File exists in a, not in b
        elif diff_item.new_file:
            file_path = diff_item.b_path  # File does not exist in a, exists in b
        else:
            # For modifications or renames, you can choose either a_path or b_path
            file_path = diff_item.a_path  # or diff_item.b_path

        # Construct the patch file path based on the chosen file path
        patch_file_path = os.path.join(patches_dir, file_path + '.patch')

        # Ensure the directory exists
        os.makedirs(os.path.dirname(patch_file_path), exist_ok=True)

        # Write the diff to the patch file
        with open(patch_file_path, 'w') as patch_file:
            patch_file.write(diff_item.diff.decode('utf-8'))

        print(f"Patch written to: {patch_file_path}")


def get_content(file, files, repo_commit, repo_info, lhs=True):
    if lhs:
        direction = 'LHS'
    else:
        direction = 'RHS'
    if file in files:
        print(f"    Processing {direction} File: {file}")
        absolute_file_path = file
        if repo_info.sub_path != '':
            absolute_file_path = repo_info.sub_path + '/' + file
        try:
            content = repo_commit.tree[absolute_file_path].data_stream.read().decode('utf-8')
        except UnicodeDecodeError:
            content = ''
    else:
        content = ''
    return content


def is_rename(str1, str2, from_str, to_str):
    # Replace "from_str" with "to_str" in str1
    renamed_str = str1.replace(from_str, to_str)

    # Check if the resulting strings are equal
    return renamed_str == str2


def generate_diffs_between_repo_and_upstream(target_repo_info: RepoInfo, upstream_repo_info: RepoInfo, output_dir: str):
    target_repo = Repo(target_repo_info.repo_path)
    target_repo_commit = target_repo.commit(target_repo_info.branch)

    upstream_repo = Repo(upstream_repo_info.repo_path)
    upstream_repo_commit = upstream_repo.commit(upstream_repo_info.branch)

    if target_repo_info.sub_path == '':
        target_tree = target_repo_commit.tree
    else:
        target_tree = target_repo_commit.tree[target_repo_info.sub_path]

    if upstream_repo_info.sub_path == '':
        upstream_tree = upstream_repo_commit.tree
    else:
        upstream_tree = upstream_repo_commit.tree[upstream_repo_info.sub_path]

    # Create filtered sets of relative file paths for LHS and RHS
    lhs_files = set()
    for blob in target_tree.traverse():
        if blob.type == 'blob':
            rel_path = os.path.relpath(blob.path, target_repo_info.sub_path)
            lhs_files.add(rel_path)

    rhs_files = set()
    for blob in upstream_tree.traverse():
        if blob.type == 'blob':
            rel_path = os.path.relpath(blob.path, upstream_repo_info.sub_path)
            rhs_files.add(rel_path)

    # Find the union of files between LHS and RHS
    common_files = lhs_files.union(rhs_files)

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate and save patch diffs for each common file
    for file in common_files:
        print(f"Processing file: {file}")
        lhs_content = get_content(file, lhs_files, target_repo_commit, target_repo_info, lhs=True)
        rhs_content = get_content(file, rhs_files, upstream_repo_commit, upstream_repo_info, lhs=False)

        # Perform a unified diff between LHS and RHS content
        diff = difflib.unified_diff(lhs_content.splitlines(), rhs_content.splitlines(), lineterm='')
        # Convert the diff to a string
        diff_str = '\n'.join(diff)
        if diff_str != '':
            # process this diff against all renames...

            # Create the patch file path
            patch_file_path = os.path.join(output_dir, file + '.patch')

            os.makedirs(os.path.dirname(patch_file_path), exist_ok=True)

            # Save the patch diff to the file
            with open(patch_file_path, 'w') as patch_file:
                patch_file.write(diff_str)
        else:
            print(f"    ******* No diff: {file}")


# def prune_diffs(diff_bs, your_custom_rules):
#     # TODO: Implement your custom pruning logic based on rules
#     pruned_diffs = {}
#     for file, diff in diff_bs.items():
#         pruned_diff = apply_your_rules_to_diff(diff, your_custom_rules)
#         pruned_diffs[file] = pruned_diff
#     return pruned_diffs
#
#
# def apply_your_rules_to_diff(diff, rules):
#     # TODO: Implement the actual rule-based diff transformation
#     return diff  # Placeholder
#
#
# def cross_reference_diffs(diff_a, pruned_diff_bs):
#     # TODO: Implement the logic to cross-reference and eliminate overlapping changes
#     final_diffs = {}
#     # Placeholder code
#     for file, pruned_diff in pruned_diff_bs.items():
#         if file in diff_a:
#             final_diffs[file] = resolve_overlaps(diff_a[file], pruned_diff)
#     return final_diffs
#
#
# def resolve_overlaps(diff_a, pruned_diff_b):
#     # TODO: Implement the actual logic to resolve overlaps
#     return pruned_diff_b  # Placeholder
#
#
# def apply_diffs(repo_path, final_diffs):
#     repo = Repo(repo_path)
#     for file, diff in final_diffs.items():
#         # TODO: Determine the best way to apply these diffs (git apply, manual application, etc.)
#         pass


def main():
    # diffs = generate_upstream_diffs("/Users/shailendra/WS/deepflowio/deepflow",
    #                                 "ca3706a53ead5e8f0a5ca7574d8616f4e6c14e4b",
    #                                 "main")
    # split_diffs(diffs, "upstream_patches")

    target_repo_info = RepoInfo(repo_path="/Users/shailendra/WS/nebulaiq/nebulaiq-telemetry-agent",
                                sub_path="",
                                branch="merge_from_upstream")

    upstream_repo_info = RepoInfo(repo_path="/Users/shailendra/WS/deepflowio/deepflow",
                                  sub_path="agent",
                                  branch="main")

    generate_diffs_between_repo_and_upstream(target_repo_info, upstream_repo_info, "target_patches")


if __name__ == '__main__':
    main()

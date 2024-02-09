import os

from kwiq.core.flow import Flow
from kwiq.task.setup_3_way_merge import MergeRepoInfos, RepoInfo, SetupThreeWayMerge

from smart_code_merge.commons import AppConfig


class Setup(Flow):
    name: str = "setup"

    def fn(self, config: AppConfig) -> None:
        working_dir = config.working_dir

        # # step 1: setup 3 way merge for all projects
        for project in config.projects:
            os.chdir(working_dir)
            base_dir = (working_dir / f"__{project.key}")
            repo_infos = MergeRepoInfos(
                base=RepoInfo(
                    repo_path=project.upstream_project_git_path,
                    branch=project.upstream_project_base_branch,
                    sub_path=project.upstream_project_sub_folder,
                ),
                local=RepoInfo(
                    repo_path=project.local_project_git_path,
                    branch=project.local_project_branch,
                    sub_path=project.local_project_sub_folder,
                ),
                remote=RepoInfo(
                    repo_path=project.upstream_project_git_path,
                    branch=project.upstream_project_head_branch,
                    sub_path=project.upstream_project_sub_folder,
                ),
            )
            SetupThreeWayMerge().execute(output_dir=base_dir, repo_infos=repo_infos)

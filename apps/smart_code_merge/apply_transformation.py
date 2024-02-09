import os

from kwiq.core.flow import Flow
from kwiq.task.apply_renames import ApplyRenames
from kwiq.task.run_command import RunCommand

from smart_code_merge.commons import AppConfig


class ApplyTransformation(Flow):
    name: str = "apply-transformation"

    def fn(self, config: AppConfig) -> None:
        working_dir = config.working_dir

        mapping_file = (working_dir / "rename_mapping.csv").resolve()

        # for each project
        #   step 5: apply transformation
        #   step 6: commit code
        #   step 7: apply 3 way merge
        for project in config.projects:
            project_directory = (working_dir / f"__{project.key}" / "merge_dir").resolve()
            os.chdir(project_directory)

            # # cleaning step
            # RunCommand().execute(command="git reset --hard")

            # RunCommand().execute(command="git checkout remote")

            # cleaning step
            # RunCommand().execute(command="git reset --hard HEAD~1")

            ApplyRenames().execute(mapping_csv_path=mapping_file, search_directory=project_directory)

            RunCommand().execute(command='git add .')
            RunCommand().execute(command=f'git commit -m "post transformation version"')

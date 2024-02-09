import os

from kwiq.core.flow import Flow
from kwiq.task.apply_3_way_merge import ApplyThreeWayMerge
from smart_code_merge.commons import AppConfig


class Merge(Flow):
    name: str = "merge"

    def fn(self, config: AppConfig) -> None:
        working_dir = config.working_dir

        # for each project
        #   step 5: apply transformation
        #   step 6: commit code
        #   step 7: apply 3 way merge
        for project in config.projects:
            # # cleaning step
            # RunCommand().execute(command="git reset --hard")

            # RunCommand().execute(command="git checkout remote")

            # cleaning step
            # RunCommand().execute(command="git reset --hard HEAD~1")

            os.chdir(working_dir)
            base_dir = (working_dir / f"__{project.key}")
            ApplyThreeWayMerge().execute(base_dir=base_dir)

            # HUMAN STEP
            #   step 8: merge conflicts manually
            # HUMAN STEP

from pathlib import Path
from typing import List

from pydantic import BaseModel


class ProjectConfig(BaseModel):
    key: str
    local_project_path: Path
    local_project_git_path: str
    local_project_branch: str = "main"
    local_project_sub_folder: str = ""
    upstream_project_git_path: str
    upstream_project_base_branch: str
    upstream_project_head_branch: str = "main"
    upstream_project_sub_folder: str


class AppConfig(BaseModel):
    working_dir: Path
    projects: List[ProjectConfig]
    rename_words_regex: str

import os
import shutil

from pydantic import BaseModel


class RepoInfo(BaseModel):
    repo_path: str
    branch: str
    sub_path: str


def clean_directory(directory):
    for item in os.listdir(directory):
        path = os.path.join(directory, item)
        if os.path.isdir(path) and item != '.git':
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)

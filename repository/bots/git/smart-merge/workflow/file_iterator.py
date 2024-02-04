from pathlib import Path
from typing import Callable, Optional, List
import os
import fnmatch


class FileIterator:
    def __init__(self, directory: Path, fn: Callable[[str], None], filters: Optional[List[str]] = None):
        self.directory = directory
        self.fn = fn
        self.filters = filters or ['*']  # Default to all files if no filter is provided

    def iterate_files(self) -> None:
        for dir_path, dir_names, filenames in os.walk(self.directory):
            for filename in filenames:
                if not any(fnmatch.fnmatch(filename, pattern) for pattern in self.filters):
                    continue  # Skip files that don't match the filter pattern

                filepath = os.path.join(dir_path, filename)
                if os.path.isfile(filepath):
                    self.fn(filepath)


class FileIteratorBuilder:
    def __init__(self):
        self.directory = None
        self.process_file = None
        self.filters = None

    def with_directory(self, directory: Path) -> 'FileIteratorBuilder':
        self.directory = directory
        return self

    def with_fn(self, fn: Callable[[str], None]) -> 'FileIteratorBuilder':
        self.process_file = fn
        return self

    def with_filters(self, filters: List[str]) -> 'FileIteratorBuilder':
        self.filters = filters
        return self

    def build(self) -> FileIterator:
        if not self.directory or not self.process_file:
            raise ValueError("Directory and process_file function must be provided")
        return FileIterator(self.directory, self.process_file, self.filters)

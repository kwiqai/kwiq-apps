import csv
from pathlib import Path
from typing import Type, Iterator, List, Optional
from pydantic import BaseModel


class CSVIterator:
    def __init__(self, data_model: Type[BaseModel], file_path: Path, fieldnames: Optional[List[str]] = None,
                 has_header: bool = True):
        self.data_model = data_model
        self.file_path = file_path
        self.fieldnames = fieldnames
        self.has_header = has_header

    def __iter__(self) -> Iterator[BaseModel]:
        with open(self.file_path, mode='r') as infile:
            if self.has_header:
                csv_fieldnames = next(csv.reader(infile))
                if self.fieldnames and csv_fieldnames != self.fieldnames:
                    raise ValueError("Provided fieldnames do not match the CSV header")
                self.fieldnames = self.fieldnames or csv_fieldnames
            elif not self.fieldnames:
                raise ValueError("fieldnames must be provided when has_header is False")

            reader = csv.DictReader(infile, fieldnames=self.fieldnames)
            if self.has_header:
                next(reader, None)  # Skip the header
            for row in reader:
                yield self.data_model(**row)


class CSVIteratorBuilder:
    def __init__(self):
        self.data_model = None
        self.file_path = None
        self.fieldnames = None
        self.has_header = True

    def with_data_model(self, model: Type[BaseModel]) -> 'CSVIteratorBuilder':
        self.data_model = model
        return self

    def with_file_path(self, file_path: Path) -> 'CSVIteratorBuilder':
        self.file_path = file_path
        return self

    def with_fieldnames(self, fieldnames: List[str]) -> 'CSVIteratorBuilder':
        self.fieldnames = fieldnames
        return self

    def with_header(self, has_header: bool) -> 'CSVIteratorBuilder':
        self.has_header = has_header
        return self

    def build(self) -> CSVIterator:
        if not self.data_model or not self.file_path:
            raise ValueError("Model and file_path must be provided")
        if not self.has_header and not self.fieldnames:
            raise ValueError("fieldnames must be provided when header is False")
        return CSVIterator(self.data_model, self.file_path, self.fieldnames, self.has_header)

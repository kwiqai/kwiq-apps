import csv
from pathlib import Path
from typing import Iterator, Type, Union

from pydantic import BaseModel


def get_field_names(model_type: Type[BaseModel]) -> list:
    # Get the field names (keys) of the Pydantic model
    return list(model_type.__annotations__.keys())


def write_data_to_csv(data_iter: Union[Iterator[BaseModel], list[Type[BaseModel]]], csv_file_path: Path) -> None:
    try:
        if not isinstance(data_iter, Iterator):
            data_iter = iter(data_iter)

        # Get the first object from the iterator (assuming it's not empty)
        first_object = next(data_iter)

        if isinstance(first_object, BaseModel):
            model_type = type(first_object)
        else:
            raise ValueError("Invalid type in data_iter")

        # Get the field names for the model
        header = get_field_names(model_type)
        print("Header: ", header)

        # Write the data to the CSV file
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Write the header row
            writer.writerow(header)

            # Write the first object to the CSV
            writer.writerow([getattr(first_object, field) for field in header])

            # Write the rest of the objects in the iterator
            for data in data_iter:
                if data is not None:
                    writer.writerow([getattr(data, field) for field in header])
    except StopIteration:
        pass

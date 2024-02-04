from pydantic import BaseModel
from typing import Type, Union, Any, Optional
from abc import ABC, abstractmethod


class StepException(Exception):
    """Base exception for workflow step errors."""


class ValidationError(StepException):
    """Raised when input data validation fails."""


class ProcessingError(StepException):
    """Raised when an error occurs during the processing of a step."""


InputModelType = Union[Type[BaseModel], type, None]
OutputModelType = Union[Type[BaseModel], type, None]


class Step(ABC):
    name: str

    @property
    @abstractmethod
    def input_model(self) -> InputModelType:
        pass

    @property
    @abstractmethod
    def output_model(self) -> OutputModelType:
        pass

    def execute(self, data: Optional[Any]) -> Optional[Any]:
        # Handle input data based on input_model type
        if self.input_model is None:
            input_data = None
        elif issubclass(self.input_model, (int, float, str, bool, list, dict, tuple)):
            input_data = data
        elif issubclass(self.input_model, BaseModel):
            try:
                # Check if data is already an instance of the input model
                if isinstance(data, self.input_model):
                    input_data = data
                else:
                    input_data = self.input_model(**data)
            except ValidationError as e:
                raise ValidationError(f"Input data validation failed: {str(e)}")
        else:
            raise ValidationError(f"Unsupported type for input_model: {self.input_model}")

        # Perform the actual step logic
        result = self.fn(input_data)

        # Handle output data based on output_model type
        if self.output_model is None:
            return None  # No output expected
        elif hasattr(self.output_model, '__origin__'):
            # It's a typing generic
            if (self.output_model.__origin__ is list
                    or self.output_model.__origin__ is set
                    or self.output_model.__origin__ is dict):
                return result
        elif issubclass(self.output_model, (int, float, str, bool, list, dict, tuple)):
            return result
        elif issubclass(self.output_model, BaseModel):
            try:
                # Check if data is already an instance of the input model
                if isinstance(result, self.output_model):
                    return result
                else:
                    return self.input_model(**result)
            except ValidationError as e:
                raise ValidationError(f"Output data validation failed: {str(e)}")
        else:
            raise ValidationError(f"Unsupported type for output_model: {self.output_model}")

    @abstractmethod
    def fn(self, data: InputModelType) -> OutputModelType:
        """
        Execute the step with the given data.

        Parameters:
        - data: The input data for the step.

        Returns:
        - The output data produced by the step, if any.
        """
        pass

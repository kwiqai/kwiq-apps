from typing import Callable, Optional

from pydantic import BaseModel

from workflow.step import Step, InputModelType, OutputModelType


class InputModel(BaseModel):
    instruction: str
    validation_fn: Optional[Callable[[], bool]]


class HumanStep(Step):

    @property
    def input_model(self) -> InputModelType:
        return InputModel

    @property
    def output_model(self) -> OutputModelType:
        return bool

    def fn(self, data: InputModel) -> bool:
        """
        Displays an instruction to the user and waits for their input.
        Optionally performs some validation such as whether necessary user actions were done or not
        """
        print(f"{data.instruction}")

        while True:
            try:
                # Show the instruction to the user
                user_input = input(f"Proceed (Y/N): ").lower()
                if user_input == "y" or user_input == "yes":
                    # If a validation pattern is provided, validate the input
                    if data.validation_fn and not data.validation_fn():
                        print("Invalid input. Please try again.")
                        continue

                    # If input is valid or no validation is needed, break the loop
                    break
                else:
                    print("Waiting for your go ahead...")
            except KeyboardInterrupt:
                # Handle Ctrl-C (KeyboardInterrupt)
                print("\nOperation terminated by user (Ctrl-C).")
                return False

        # Continue with the rest of your workflow
        print("Continuing with the workflow...")
        return True

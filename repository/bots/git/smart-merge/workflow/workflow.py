from typing import List

from workflow.step import Step


# Workflow would provide ability to manage state, resume etc
class Workflow:
    name: str
    steps: List[Step]

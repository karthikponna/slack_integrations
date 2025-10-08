from loguru import logger
from typing_extensions import Annotated
from zenml import get_step_context, step

@step
def testing_step(name:str = "default_step") -> Annotated[str, "testing_step"]:
    
    print("hello from step function")

    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="testing_step",
        metadata={
            "testing_name": name
        },
    )

    return name
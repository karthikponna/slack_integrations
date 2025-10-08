from pathlib import Path

from loguru import logger
from zenml import pipeline

from steps.testing_step import testing_step

@pipeline
def testing_pipeline(name:str = "default") -> None:

    testing_step(name)
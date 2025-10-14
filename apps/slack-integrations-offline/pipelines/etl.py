from pathlib import Path

from loguru import logger
from zenml import pipeline

from steps.infrastructure.read_documents_from_disk import read_documents_from_disk


@pipeline
def etl(
    data_dir: Path = Path(),
) -> None:
    
    crawled_data_dir = data_dir / "crawled"

    documents = read_documents_from_disk(
        data_directory = crawled_data_dir, nesting_level = 0
    )

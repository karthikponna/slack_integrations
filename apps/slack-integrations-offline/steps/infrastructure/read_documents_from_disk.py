from pathlib import Path
import time
from loguru import logger

from typing_extensions import Annotated
from zenml import get_step_context, step

from src.slack_integrations_offline.config import settings
from src.slack_integrations_offline.domain.document import Document


@step
def read_documents_from_disk(
    data_directory: Path,
    nesting_level: int = 0,
)-> Annotated[list[Document],"documents"]:
    """Read Document objects from JSON files stored on disk.
    
    Args:
        data_directory: Path to the directory containing JSON files.
        nesting_level: Level of subdirectory nesting to search for JSON files.
    
    Returns:
        list[Document]: List of documents loaded from JSON files.
    """
    pages:list[Document] = []

    logger.info(f"Reading documents from '{data_directory}'")

    if not data_directory.exists():
        raise FileExistsError(f"Directory not found: '{data_directory}'")
    
    json_files = __get_json_files(data_directory= data_directory, nesting_level= nesting_level)

    for json_file in json_files:
        page = Document.from_file(json_file)

        pages.append(page)

    logger.info(f"Successfully read {len(pages)} documents from disk.")

    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="documents",
        metadata={
            "count": len(pages),
        }
    )

    return pages


def __get_json_files(data_directory: Path, nesting_level: int = 0) -> None:

    """Read Document objects from JSON files stored on disk.
    
    Args:
        data_directory: Path to the directory containing JSON files.
        nesting_level: Level of subdirectory nesting to search for JSON files.
    
    Returns:
        list[Document]: List of documents loaded from JSON files.
    """
    if nesting_level == 0:
        return list(data_directory.glob("*.json"))
    
    else:
        json_files = []

        for database_dir in data_directory.iterdir():
            if database_dir.is_dir():
                nested_json_files = __get_json_files(data_directory=database_dir, nesting_level=nesting_level-1)

                json_files.extend(nested_json_files)

        return json_files
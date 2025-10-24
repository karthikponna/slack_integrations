from pathlib import Path

from loguru import logger
from zenml import pipeline

from steps.infrastructure.read_documents_from_disk import read_documents_from_disk
from steps.generate_summaries.generate_summary import generate_summary
from steps.infrastructure.save_documents_to_disk import save_documents_to_disk
from steps.infrastructure.ingest_to_mongodb import ingest_to_mongodb

from src.slack_integrations_offline.domain.document import Document

@pipeline
def etl(
    summarization_model: str,
    load_collection_name: str,
    data_dir: Path = Path(),
    temperature: float = 0.0,
    max_workers: int = 10,
    summarization_max_characters: int = 1000,
) -> None:
    
    crawled_data_dir = data_dir / "crawled"

    enhanced_data_dir = data_dir / "enhanced"

    documents = read_documents_from_disk(
        data_directory = crawled_data_dir, nesting_level = 0
    )

    enhanced_documents = generate_summary(
        summarization_model=summarization_model,
        documents=documents,
        temperature=temperature,
        max_workers=max_workers,
        summarization_max_characters=summarization_max_characters,
    )

    save_documents_to_disk(documents=enhanced_documents, output_dir=enhanced_data_dir)
    

    ingest_to_mongodb(
        models=enhanced_documents,
        collection_name=load_collection_name,
        clear_collection=True
    )
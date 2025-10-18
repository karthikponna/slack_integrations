from loguru import logger
from typing_extensions import Annotated
from zenml import get_step_context, step

from src.slack_integrations_offline.domain.document import Document
from src.slack_integrations_offline.applications.summary import SummarizationGenerator


@step
def generate_summary(
    summarization_model: str,
    documents: list[Document],
    temperature: float = 0.0,
    max_workers: int = 10,
    min_document_length: int = 50,
    summarization_max_characters: int = 1000,

) -> Annotated[list[Document],"summary"]:
    
    summary_generator = SummarizationGenerator(
        summarization_model=summarization_model,
        summarization_max_characters=summarization_max_characters,
        max_workers=max_workers,
        min_document_length=min_document_length,
    )

    summaries = summary_generator.generate(documents=documents, temperature=temperature)

    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="summary",
        metadata={
            "len of summaries generated": len(summaries)
        }
    )

    return summaries
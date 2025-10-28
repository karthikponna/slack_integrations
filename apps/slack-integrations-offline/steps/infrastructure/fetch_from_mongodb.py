from loguru import logger

from pydantic import BaseModel

from typing_extensions import Annotated
from zenml import get_step_context, step

from src.slack_integrations_offline.domain.document import Document
from src.slack_integrations_offline.infrastructure.mongodb.service import MongoDBService


@step
def fetch_from_mongodb(
    collection_name: str, 
    limit: int,
) -> Annotated[list[dict], "documents"]:
    
    with MongoDBService(model=Document, collection_name=collection_name) as service:
        documents =service.fetch_documents(limit=limit, query={})


    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="documents",
        metadata={
            "count": len(documents),
        },
    )

    return documents

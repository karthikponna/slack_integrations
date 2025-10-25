from loguru import logger
from typing import Callable

from src.slack_integrations_offline.domain.document import Document
from src.slack_integrations_offline.applications.agents.summarization import SummarizationAgent


class SummarizationGenerator:
    
    def __init__(
        self,
        summarization_model: str,
        summarization_max_characters: int,
        max_workers: int = 10,
        min_document_length: int = 50,
    ) -> None:
        self.summarization_model = summarization_model
        self.summarization_max_characters = summarization_max_characters
        self.max_workers = max_workers
        self.min_document_length = min_document_length

        self.pregeneration_filters: list[Callable[[Document], bool]] = [
            lambda document: len(document.content) > self.min_document_length
        ]

        self.postgeneration_filters: list[Callable[[Document], bool]] = [
            lambda document: document.summary is not None
        ]

    
    def generate(self, documents: list[Document], temperature: float = 0.0) -> list[Document]:

        if len(documents) < 10:
            logger.warning(
                "Less than 10 documents to summarize. For accurate behavior we recommend having at least 10 documents."
            )

        filtered_summarized_documents = self.__summarize_documents(documents, temperature=temperature)

        logger.info(f"No. of final filtered summarized documents {len(filtered_summarized_documents)}")

        return filtered_summarized_documents

    
    def __summarize_documents(
        self, documents: list[Document], temperature: float = 0.0
        ) -> list[Document]:

        logger.info(f"No. of documents before pregeneration filtering: {len(documents)}")

        filtered_documents = self.filtered_documents(
            self.pregeneration_filters, documents
        )
        logger.info(
            f"No. of documents after pregeneration filtering: {len(filtered_documents)}"
        )

        summarized_documents: list[Document] = self.__summarization(
            filtered_documents, temperature
        )
        logger.info(
            f"No. of documents before postgeneration filtering: {len(summarized_documents)}"
        )

        filtered_summarized_documents = self.filtered_documents(
            self.postgeneration_filters, summarized_documents
        )
        logger.info(
            f"No. of documents after postgeneration filtering: {len(filtered_summarized_documents)}"
        )
        
        return filtered_summarized_documents




    def filtered_documents(
        self, filters: list[Callable[[Document], bool]], documents: list[Document],
    ) -> list[Document]:
        
        for document_filter in filters:
            documents = [
                document for document in documents if document_filter(document)
            ]

        return documents
    

    def __summarization(
        self, documents: list[Document], temperature: float = 0.0
    ) -> list[Document]:
        
        summarization_agent = SummarizationAgent(
            max_characters=self.summarization_max_characters,
            model_id=self.summarization_model,
            max_concurrent_requests=self.max_workers
        )

        logger.info(f"Summarizing {len(documents)} documents with temperature {temperature}")

        summarized_documents = summarization_agent(documents, temperature)

        valid_summarized_documents = [
            doc for doc in summarized_documents if doc.summary is not None
        ]

        logger.info(f"Successfully summarized {len(valid_summarized_documents)} documents")

        return valid_summarized_documents
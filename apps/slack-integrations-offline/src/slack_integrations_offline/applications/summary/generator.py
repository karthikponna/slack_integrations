from loguru import logger
from typing import Callable

from src.slack_integrations_offline.domain.document import Document
from src.slack_integrations_offline.applications.agents.summarization import SummarizationAgent


class SummarizationGenerator:
    """Generator for creating summaries of documents with pre and post-generation filtering.
    
    Manages the end-to-end summarization workflow including document filtering, batch summarization, and validation.
    
    Attributes:
        summarization_model: Identifier for the language model to use for summarization.
        summarization_max_characters: Maximum character length for generated summaries.
        max_workers: Maximum number of concurrent workers for parallel processing.
        min_document_length: Minimum character length for documents to be summarized.
        pregeneration_filters: List of filter functions applied before summarization.
        postgeneration_filters: List of filter functions applied after summarization.
    """

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
        """Generate summaries for a list of documents with filtering and validation.
    
        Args:
            documents: List of documents to generate summaries for.
            temperature: Sampling temperature for text generation.
        
        Returns:
            list[Document]: List of documents with successfully generated and validated summaries.
        """

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
        """Apply pre-generation filters, summarize documents, and apply post-generation filters.
    
        Args:
            documents: List of documents to process.
            temperature: Sampling temperature for text generation.
        
        Returns:
            list[Document]: List of filtered documents with valid summaries.
        """
        
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
        """Apply a series of filter functions to documents sequentially.
    
        Args:
            filters: List of callable filter functions that take a Document and return a boolean.
            documents: List of documents to filter.
        
        Returns:
            list[Document]: List of documents that passed all filter criteria.
        """
        
        for document_filter in filters:
            documents = [
                document for document in documents if document_filter(document)
            ]

        return documents
    

    def __summarization(
        self, documents: list[Document], temperature: float = 0.0
    ) -> list[Document]:
        """Execute the summarization process using SummarizationAgent.
    
        Args:
            documents: List of documents to summarize.
            temperature: Sampling temperature for text generation.
        
        Returns:
            list[Document]: List of documents with generated summaries, excluding failed attempts.
        """

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
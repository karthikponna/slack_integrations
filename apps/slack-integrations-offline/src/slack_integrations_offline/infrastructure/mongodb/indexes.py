from langchain_mongodb.index import create_fulltext_search_index

from src.slack_integrations_offline.infrastructure.mongodb.service import MongoDBService


class MongodbIndex:
    """Manager for creating and configuring MongoDB vector search indexes.
    
    Handles creation of vector search indexes and optional full-text search indexes for hybrid retrieval.
    
    Attributes:
        retriever: Retriever instance containing the vector store configuration.
        mongodb_client: MongoDBService instance for database operations.
    """
    def __init__(
        self,
        retriever,
        mongodb_client: MongoDBService,
    ) -> None:
        self.retriever = retriever
        self.mongodb_client = mongodb_client


    def create(
        self,
        embedding_dims: int,
        is_hybrid: bool = False,
    ) -> None:
        """Create vector search index and optionally full-text search index in MongoDB.
    
        Args:
            embedding_dims: Dimensionality of the embedding vectors for the index.
            is_hybrid: Whether to create additional full-text search index for hybrid retrieval.
        """
        
        vectorstore = self.retriever.vectorstore

        vectorstore.create_vector_search_index(
            dimensions=embedding_dims,
        )

        if is_hybrid:
            create_fulltext_search_index(
                collection=self.mongodb_client.collection,
                field=vectorstore._text_key,
                index_name=self.retriever.search_index_na
            )
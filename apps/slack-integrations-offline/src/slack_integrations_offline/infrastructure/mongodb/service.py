from typing import Generic, Type, TypeVar
from bson import ObjectId

from loguru import logger
from pydantic import BaseModel
from pymongo import MongoClient, errors

from src.slack_integrations_offline.config import settings

T = TypeVar("T", bound=BaseModel)


class MongoDBService(Generic[T]):
    """Generic service for MongoDB operations with Pydantic model support.
    
    Provides database operations including ingestion, fetching, and collection management with automatic model validation.
    
    Attributes:
        model: Pydantic model type for document validation.
        collection_name: Name of the MongoDB collection.
        database_name: Name of the MongoDB database.
        mongodb_uri: MongoDB connection URI.
        client: MongoClient instance for database connection.
        database: MongoDB database instance.
        collection: MongoDB collection instance.
    """

    def __init__(
        self,
        model: Type[T],
        collection_name: str,
        database_name: str = settings.MONGODB_DATABASE_NAME,
        mongodb_uri: str = settings.MONGODB_URI,
    ) -> None:
        
        self.model = model
        self.collection_name = collection_name
        self.database_name = database_name
        self.mongodb_uri = mongodb_uri

        try: 
            self.client = MongoClient(mongodb_uri, appname="slack_integrations")
            self.client.admin.command("ping")

        except Exception as e:
            logger.error(f"Failed to initialize MongoDBService: {e}")
            raise

        self.database = self.client[database_name]
        self.collection = self.database[collection_name]

        logger.info(
            f"Connected to MongoDB instance:\n URI: {mongodb_uri}\n Database: {database_name}\n Collection: {collection_name}"
        )

    
    def __enter__(self) -> "MongoDBService":
        """Enter context manager and return the service instance.
    
        Returns:
            MongoDBService: The service instance for use in context.
        """
        return self
    

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager and close database connection.
    
        Args:
            exc_type: Exception type if an exception occurred.
            exc_val: Exception value if an exception occurred.
            exc_tb: Exception traceback if an exception occurred.
        """
        self.close()


    def clear_collection(self) -> None:
        """Delete all documents from the collection.
    
        Returns:
            None
        
        Raises:
            errors.PyMongoError: If deletion operation fails.
        """
        
        try:
            result = self.collection.delete_many({})
            logger.debug(
                f"Cleared collection. Deleted {result.deleted_count} documents."
            )
        
        except errors.PyMongoError as e:
            logger.error(f"Error clearing the collection: {e}")
            raise

    
    def ingest_documents(self, documents: list[T]) -> None:
        """Insert multiple Pydantic model documents into the collection.
    
        Args:
            documents: List of Pydantic model instances to insert.
        
        Returns:
            None
        
        Raises:
            ValueError: If documents are not valid Pydantic models.
            errors.PyMongoError: If insertion operation fails.
        """
        
        try:
            if not documents or not all(isinstance(doc, BaseModel) for doc in documents):
                raise ValueError("Documents must be a list of Pydantic models.")
            
            dict_documents = [ doc.model_dump() for doc in documents]

            for doc in dict_documents:
                doc.pop("_id", None)

            self.collection.insert_many(dict_documents)
            logger.debug(f"Inserted {len(documents)} documents into MongoDB.")

        except errors.PyMongoError as e:
            logger.error(f"Error inserting documents: {e}")
            raise


    def fetch_documents(self, limit: int | None = None, query: dict = None) -> list[T]:
        """Fetch documents from collection and parse them into Pydantic models.
    
        Args:
            limit: Maximum number of documents to fetch. None for no limit. Defaults to None.
            query: MongoDB query filter dictionary. Defaults to None.
        
        Returns:
            list[T]: List of parsed Pydantic model instances.
        """
        
        try:
            documents = list(self.collection.find(query).limit(limit or 0))
            logger.debug(f"Fetched {len(documents)} documents with query: {query}")

            return self.__parsed_documents(documents)
        
        except Exception as e:
            logger.error(f"Error fetching documents: {e}")
            raise

    
    def __parsed_documents(self, documents: list[dict]) -> list[T]:
        """Parse raw MongoDB documents into validated Pydantic model instances.
    
        Args:
            documents: List of raw MongoDB document dictionaries.
        
        Returns:
            list[T]: List of validated Pydantic model instances.
        """
        
        parsed_documents = []
        for doc in documents:
            for key, value in doc.items():
                if isinstance(value, ObjectId):
                    doc[key] = str(value)

            _id = doc.pop("_id", None)
            doc["id"] = _id

            parsed_doc = self.model.model_validate(doc)
            parsed_documents.append(parsed_doc)
        
        return parsed_documents
    

    def get_collection_count(self) -> int:
        """Get the total count of documents in the collection.
    
        Returns:
            int: Number of documents in the collection.
        
        Raises:
            errors.PyMongoError: If count operation fails.
        """
        
        try:
            count = self.collection.count_documents({})
            return count
        except errors.PyMongoError as e:
            logger.error(f"Error counting documents in MongoDB: {e}")
            raise

        
    def close(self) -> None:
        """Close the MongoDB client connection."""
        
        self.client.close()
        logger.debug("Closed MongoDB connection.")
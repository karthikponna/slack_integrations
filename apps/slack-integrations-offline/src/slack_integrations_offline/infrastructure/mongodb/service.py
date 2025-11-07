from typing import Generic, Type, TypeVar
from bson import ObjectId

from loguru import logger
from pydantic import BaseModel
from pymongo import MongoClient, errors

from src.slack_integrations_offline.config import settings

T = TypeVar("T", bound=BaseModel)


class MongoDBService(Generic[T]):
    

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

        return self
    

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:

        self.close()


    def clear_collection(self) -> None:

        try:
            result = self.collection.delete_many({})
            logger.debug(
                f"Cleared collection. Deleted {result.deleted_count} documents."
            )
        
        except errors.PyMongoError as e:
            logger.error(f"Error clearing the collection: {e}")
            raise

    
    def ingest_documents(self, documents: list[T]) -> None:
        
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

        try:
            documents = list(self.collection.find(query).limit(limit or 0))
            logger.debug(f"Fetched {len(documents)} documents with query: {query}")

            return self.__parsed_documents(documents)
        
        except Exception as e:
            logger.error(f"Error fetching documents: {e}")
            raise

    
    def __parsed_documents(self, documents: list[dict]) -> list[T]:

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

        try:
            count = self.collection.count_documents({})
            return count
        except errors.PyMongoError as e:
            logger.error(f"Error counting documents in MongoDB: {e}")
            raise

        
    def close(self) -> None:

        self.client.close()
        logger.debug("Closed MongoDB connection.")
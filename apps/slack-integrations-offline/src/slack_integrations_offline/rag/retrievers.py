from langchain_openai import OpenAIEmbeddings

from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_mongodb.retrievers.hybrid_search import MongoDBAtlasHybridSearchRetriever

from src.slack_integrations_offline.rag.embeddings import get_openai_embedding_model
from src.slack_integrations_offline.config import settings


def get_retriever(
    embedding_model_id: str, k: int = 3
) -> MongoDBAtlasHybridSearchRetriever:
    """Create a MongoDB Atlas hybrid search retriever with specified embedding model.
    
    Args:
        embedding_model_id: Identifier for the OpenAI embedding model to use.
        k: Number of top results to retrieve. Defaults to 3.
    
    Returns:
        MongoDBAtlasHybridSearchRetriever: Configured hybrid search retriever instance.
    """
    embedding_model = get_openai_embedding_model(model_id=embedding_model_id)

    return get_hybrid_search_retriever(embedding_model=embedding_model, k=k)



def get_hybrid_search_retriever(
    embedding_model: OpenAIEmbeddings, k: int = 3
) -> MongoDBAtlasHybridSearchRetriever:
    """Create a MongoDB Atlas hybrid search retriever combining vector and full-text search.
    
    Args:
        embedding_model: OpenAI embeddings model instance for vector search.
        k: Number of top results to retrieve. Defaults to 3.
    
    Returns:
        MongoDBAtlasHybridSearchRetriever: Configured retriever with balanced vector and full-text penalties.
    """
    
    vectorstore = MongoDBAtlasVectorSearch.from_connection_string(
        connection_string=settings.MONGODB_URI,
        embedding=embedding_model,
        namespace=f"{settings.MONGODB_DATABASE_NAME}.rag",
        text_key="chunk",
        embedding_key="embedding",
        relevance_score_fn="dotProduct"
    )

    retriever = MongoDBAtlasHybridSearchRetriever(
        vectorstore=vectorstore,
        search_index_name="chunk_text_search",
        top_k=k,
        vector_penalty=50,
        fulltext_penalty=50
    )

    return retriever
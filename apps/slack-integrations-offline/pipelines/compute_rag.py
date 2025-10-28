from zenml import pipeline

from steps.infrastructure.fetch_from_mongodb import fetch_from_mongodb
from steps.compute_rag.chunk_embed_load import chunk_embed_load


@pipeline
def compute_rag(
    extract_collection_name: str,
    new_collection_name: str,
    embedding_model_id: str,
    embedding_model_dim: int,
    retriever_type: str,
    chunk_size: int,
    top_k: int,
    processing_batch_size: int,
    processing_max_workers: int,
    limit: int,
) -> None:
    
    documents = fetch_from_mongodb(collection_name=extract_collection_name, limit=limit)

    chunk_embed_load(
        documents=documents,
        collection_name=new_collection_name,
        embedding_model_id=embedding_model_id, 
        embedding_model_dim=embedding_model_dim,
        retriever_type=retriever_type, 
        chunk_size=chunk_size,
        top_k=top_k,
        processing_batch_size=processing_batch_size,
        processing_max_workers=processing_max_workers,
    )
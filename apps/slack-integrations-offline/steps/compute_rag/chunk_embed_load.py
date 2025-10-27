
from zenml import step

from src.slack_integrations_offline.rag.splitters import get_splitter
from src.slack_integrations_offline.rag.retrievers import get_retriever


@step
def chunk_embed_load(
    chunk_size: int,
    embedding_model_id: str, 
    top_k: int,
) -> None:
    
    splitter = get_splitter(chunk_size=chunk_size)

    retriever = get_retriever(embedding_model_id=embedding_model_id, k=top_k)
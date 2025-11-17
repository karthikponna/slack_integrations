from typing import Any, Generator
from concurrent.futures import ThreadPoolExecutor, as_completed

from loguru import logger
from tqdm import tqdm
from zenml import step

from langchain_core.documents import Document as LangChainDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.slack_integrations_offline.rag.splitters import get_splitter
from src.slack_integrations_offline.rag.retrievers import get_retriever

from src.slack_integrations_offline.infrastructure.mongodb.service import MongoDBService
from src.slack_integrations_offline.infrastructure.mongodb.indexes import MongodbIndex

from src.slack_integrations_offline.domain.document import Document



@step
def chunk_embed_load(
    documents: list[Document],
    collection_name: str,
    embedding_model_id: str, 
    embedding_model_dim: int,
    retriever_type: str, 
    chunk_size: int,
    top_k: int,
    processing_batch_size: int,
    processing_max_workers: int,
) -> None:
    
    """Chunk documents, generate embeddings, and load them into MongoDB with vector index.
    
    Args:
        documents: List of documents to process.
        collection_name: Name of the MongoDB collection to store documents.
        embedding_model_id: Identifier for the embedding model to use.
        embedding_model_dim: Dimensionality of the embedding vectors.
        retriever_type: Type of retriever to use for vector search.
        chunk_size: Size of text chunks for splitting documents.
        top_k: Number of top results to retrieve in searches.
        processing_batch_size: Number of documents to process in each batch.
        processing_max_workers: Maximum number of concurrent workers for processing.
    """
    
    splitter = get_splitter(chunk_size=chunk_size)

    retriever = get_retriever(embedding_model_id=embedding_model_id, k=top_k)

    with MongoDBService(
        model=Document, collection_name=collection_name
    ) as mongodb_client:
        
        mongodb_client.clear_collection()

        docs = [
            LangChainDocument(
                page_content=doc.content, metadata=doc.metadata.model_dump()
            )
            for doc in documents
            if doc
        ]

        process_docs(
            docs=docs,
            retriever=retriever,
            splitter=splitter,
            batch_size=processing_batch_size,
            max_workers=processing_max_workers,
        )

        index = MongodbIndex(
            retriever=retriever,
            mongodb_client=mongodb_client
        )

        index.create(
            embedding_dims=embedding_model_dim,
            is_hybrid=retriever_type == "contextual",
        )



def process_docs(
    docs: LangChainDocument,
    retriever: Any,
    splitter: RecursiveCharacterTextSplitter,
    batch_size: int = 4,
    max_workers: int = 2,
) -> None:
    """Process documents in parallel batches by splitting and embedding them.
    
    Args:
        docs: List of LangChain documents to process.
        retriever: Retriever instance for generating and storing embeddings.
        splitter: Text splitter for chunking documents.
        batch_size: Number of documents to process in each batch.
        max_workers: Maximum number of concurrent workers.
    """
    batches = list(get_batches(docs=docs, batch_size=batch_size))
    results = []

    total_docs = len(docs)


    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        futures = [
            executor.submit(process_batch, splitter, batch, retriever)
            for batch in batches
        ]

        with tqdm(total=total_docs, desc="Processing documents") as pbar:
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                pbar.update(batch_size)

    return results




def get_batches(
    docs: list[LangChainDocument], batch_size: int
) -> Generator[list[LangChainDocument], None, None]:
    """Generate batches of documents for parallel processing.
    
    Args:
        docs: List of LangChain documents to batch.
        batch_size: Number of documents per batch.
    
    Yields:
        Generator[list[LangChainDocument], None, None]: Batches of documents.
    """
    for i in range(0, len(docs), batch_size):
        yield docs[i : i + batch_size]



def process_batch(
    splitter: RecursiveCharacterTextSplitter,
    batch: list[LangChainDocument],
    retriever: Any,
) -> None:
    """Process a single batch of documents by splitting and adding to vector store.
    
    Args:
        splitter: Text splitter for chunking documents.
        batch: Batch of LangChain documents to process.
        retriever: Retriever instance containing the vector store.
    """
    try:
        split_docs = splitter.split_documents(batch)
        retriever.vectorstore.add_documents(split_docs)

        logger.info(f"Successfully processed {len(batch)} documents.")

    except Exception as e:
        logger.warning(f"Error processing batch of {len(batch)} documents: {str(e)}")
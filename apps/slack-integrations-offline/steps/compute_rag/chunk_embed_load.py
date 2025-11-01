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
    
    for i in range(0, len(docs), batch_size):
        yield docs[i : i + batch_size]



def process_batch(
    splitter: RecursiveCharacterTextSplitter,
    batch: list[LangChainDocument],
    retriever: Any,
) -> None:
    
    try:
        split_docs = splitter.split_documents(batch)
        retriever.vectorstore.add_documents(split_docs)

        logger.info(f"Successfully processed {len(batch)} documents.")

    except Exception as e:
        logger.warning(f"Error processing batch of {len(batch)} documents: {str(e)}")
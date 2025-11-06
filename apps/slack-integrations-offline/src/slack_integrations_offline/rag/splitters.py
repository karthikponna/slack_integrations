from loguru import logger

from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_splitter(
    chunk_size: int
) -> RecursiveCharacterTextSplitter:
    
    chunk_overlap = int(0.15 * chunk_size)

    logger.info(
        f"Getting splitter with chunk size: {chunk_size} and overlap: {chunk_overlap}"
    )
    
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        separators=["```\n", "\n\n", "\n", " ", ""] # in this order
    )
from loguru import logger

from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_splitter(
    chunk_size: int
) -> RecursiveCharacterTextSplitter:
    """Create a recursive character text splitter with tiktoken encoding.
    
    Args:
        chunk_size: Maximum size of each text chunk in tokens.
    
    Returns:
        RecursiveCharacterTextSplitter: Configured text splitter with 15% overlap and hierarchical separators.
    """
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
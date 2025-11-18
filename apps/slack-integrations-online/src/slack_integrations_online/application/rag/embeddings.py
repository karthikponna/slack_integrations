from langchain_openai import OpenAIEmbeddings

from src.slack_integrations_online.config import settings


def get_openai_embedding_model(
    model_id: str
) -> OpenAIEmbeddings:
    """Create and configure an OpenAI embeddings model instance.
    
    Args:
        model_id: Identifier for the OpenAI embedding model to use.
    
    Returns:
        OpenAIEmbeddings: Configured OpenAI embeddings model instance.
    """
    
    return OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY,
        model=model_id,
        allowed_special={"<|endoftext|>"},
    )
from langchain_openai import OpenAIEmbeddings

from src.slack_integrations_offline.config import settings


def get_openai_embedding_model(
    model_id: str
) -> OpenAIEmbeddings:
    
    return OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY,
        model=model_id,
        allowed_special={"<|endoftext|>"},
    )
import os

from agents import function_tool

from src.slack_integrations_online.application.rag.retrievers import get_retriever
from src.slack_integrations_online.application.rag.single_document_retriever import get_single_document
# from src.slack_integrations_online.utils import load_yaml_file


@function_tool
def mongodb_retriever_tool(query: str) -> str:

    """Retrieve relevant documents from MongoDB based on a search query.

    This function performs a semantic search using MongoDB's vector search capabilities
    to find the most relevant documents matching the input query. It retrieves documents,
    formats them with their metadata, and returns them in a structured XML format.

    Args:
        query: The search query string to find relevant documents.
    """

    try:
        retriever = get_retriever(embedding_model_id="text-embedding-3-small", k=3)

        relevant_docs = retriever.invoke(query)

        formatted_docs = []

        for i, doc in enumerate(relevant_docs, 1):
            formatted_docs.append(
                f"""
<document id="{i}">
<title>{doc.metadata.get("title")}</title>
<url>{doc.metadata.get("url")}</url>
<content>{doc.page_content.strip()}</content>
</document>
                """
            )

        result = "\n".join(formatted_docs)
        result = f"""
<search_results>
{result}
</search_results>
When using context from any document, also include the document URL as reference, which is found in the <url> tag.
"""     
        
        return result
    
    except Exception as e:
        print(f"error: {e}")



@function_tool
def get_complete_docs_with_url(url: str) -> str:

    """
    Retrieve the complete document content from MongoDB's raw collection using a URL.

    This tool should be used when the chunk documents retrieved from mongodb_retriever_tool
    are relevant to the user's query but lack sufficient detail or context to provide a 
    comprehensive answer. It fetches the full, untruncated document from the raw collection.

    Args:
        url: The document URL to retrieve. This URL should be obtained from the <url> tag
            in the documents returned by mongodb_retriever_tool.
    """

    document = get_single_document(url=url)

    return document
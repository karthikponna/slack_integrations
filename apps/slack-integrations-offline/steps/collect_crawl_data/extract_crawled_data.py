from loguru import logger
from typing_extensions import Annotated
from zenml import get_step_context, step

from src.slack_integrations_offline.applications.crawlers import Crawl4AICrawler
from src.slack_integrations_offline.domain import Document

@step
def extract_crawled_data(
    urls: list[str], max_workers:int = 10
) -> Annotated[list[Document], "crawled_documents"]:
    
    """Extract content from multiple URLs using web crawling.

    Args:
        urls: List of URLs to crawl.
        max_workers: Maximum number of concurrent crawling requests.

    Returns:
        list[Document]: List of documents with their extracted content from crawled pages.
    """
    
    try:
        logger.info(f"Starting crawl with {len(urls)} URLs")
        crawler = Crawl4AICrawler(max_concurrent_requests=max_workers)

        pages = crawler(urls)
        logger.info(f"Crawler returned: {type(pages)}")

        if pages is None:
            logger.error("Crawler returned None!")
            return []

        augmented_pages = list(set(pages))

        logger.info(f"Number of urls for crawling {len(urls)}.")
        logger.info(f"After crawling, we have a total of {len(augmented_pages)} documents.")

        step_context = get_step_context()
        step_context.add_output_metadata(
            output_name="crawled_documents",
            metadata={
                "no_urls_for_crawling": len(urls),
                "len_documents_after_crawling": len(augmented_pages),
            }
        )

        return augmented_pages
    
    except Exception as e:
        logger.error(f"Error in extract_crawled_data: {e}")
        logger.exception("Full traceback:")
        raise
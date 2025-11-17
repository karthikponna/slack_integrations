import asyncio
import os
import psutil
from loguru import logger
from typing import List

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

from src.slack_integrations_offline.domain.document import Document, DocumentMetadata
from src.slack_integrations_offline.utils import generate_random_hex



class Crawl4AICrawler:
    """A crawler implementation using crawl4ai library for concurrent web crawling.

    Attributes:
        max_concurrent_requests: Maximum number of concurrent HTTP requests allowed.
    """

    def __init__(self, max_concurrent_requests:int = 10) -> None:
        
        self.max_concurrent_requests = max_concurrent_requests


    def __call__(self, urls: list[str]) -> list[Document]:
        """Crawl multiple URLs and extract their content as Document objects.
    
        Args:
            urls: List of URLs to crawl.
        
        Returns:
            list[Document]: List of successfully crawled documents with extracted content.
        """

        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            return asyncio.run(self.__crawl_batch(urls))
        
        else:
            return loop.run_until_complete(self.__crawl_batch(urls))


    async def __crawl_batch(self, urls:list[str]) -> list[Document]:
        """Process a batch of URLs concurrently with semaphore-controlled crawling.
    
        Args:
            urls: List of URLs to crawl in batch.
        
        Returns:
            list[Document]: List of successfully crawled documents, excluding failed attempts.
        """

        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss

        logger.debug(
            f"Starting crawl batch with {self.max_concurrent_requests} concurrent requests. "
            f"Current process memory usage: {start_memory // (1024 * 1024)} MB"
        )


        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        final_results = []

        async with AsyncWebCrawler(cache_mode = CacheMode.BYPASS) as crawler:
            tasks = [
                self.__crawl_url(url, crawler, semaphore)
                for url in urls
            ]
            results = await asyncio.gather(*tasks)
            final_results.extend(results)
            

        end_memory = process.memory_info().rss
        crawling_memory_diff = end_memory - start_memory

        logger.debug(
            f"Crawl batch completed. "
            f"Final process memory usage: {end_memory // (1024 * 1024)} MB, "
            f"Crawling memory diff: {crawling_memory_diff // (1024 * 1024)} MB"
        )

        successful_results = [result for result in final_results if result is not None]
        
        success_count = len(successful_results)
        failed_count = len(final_results) - success_count
        total_count = len(final_results)

        logger.info(
            f"Crawling completed: "
            f"{success_count}/{total_count} succeeded ✓ | "
            f"{failed_count}/{total_count} failed ✗"
        )

        return successful_results


    async def __crawl_url(
        self, 
        url:str,
        crawler:AsyncWebCrawler,
        semaphore: asyncio.Semaphore,
    ) -> Document | None:
        """Crawl a single URL and extract its content as a Document.
    
        Args:
            url: URL to crawl.
            crawler: AsyncWebCrawler instance for performing the crawl operation.
            semaphore: Semaphore for controlling concurrent request limits.
        
        Returns:
            Document | None: Document object with extracted content, or None if crawling failed.
        """
        
        md_generator = DefaultMarkdownGenerator(
            options={
                "ignore_links": True,
                "escape_html": False,
                "ignore_images": True,
            }
        )

        config = CrawlerRunConfig(
            markdown_generator=md_generator
        )

        async with semaphore:
            result = await crawler.arun(url=url, config=config)
            await asyncio.sleep(0.5)

            if not result or not result.success:
                logger.warning(f"Failed to crawl {url}")

            if result.markdown is None:
                logger.warning(f"Failed to crawl {url}")

            
            child_links = [
                link["href"]
                for link in result.links["internal"] + result.links["external"]
            ]
            child_links_count = len(child_links)

            logger.info(f"No. of child urls {child_links_count}")

            if result.metadata:
                title = result.metadata.pop("title", "") or ""
            else:
                title = ""

            document_id = generate_random_hex(length=32)

            return Document(
                id = document_id,
                metadata = DocumentMetadata(
                    id = document_id,
                    url = url,
                    title = title,
                    properties = result.metadata or {},
                ),
                content = str(result.markdown),
                child_urls= child_links,
            )

            
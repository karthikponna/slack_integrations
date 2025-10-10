import asyncio
from crawl4ai import AsyncWebCrawler
from loguru import logger


async def main(url):
    # Create an instance of AsyncWebCrawler
    async with AsyncWebCrawler() as crawler:
        # Run the crawler on a URL
        result = await crawler.arun(url= url)
        print(result.success)
        print("*" * 50)

        if not result or not result.success:
            logger.warning(f"Failed to crawl {url}")
            
            return None

        if result.markdown is None:
            logger.warning(f"Failed to crawl {url}")
            return None

        child_links = [
            link["href"]
            for link in result.links["internal"] + result.links["external"]
        ]

        print(child_links)
        print("-"*50)
        print(result.metadata)

        if result.metadata:
            title = result.metadata.pop("title", "") or ""
        else:
            title = ""

        
        if result:
            with open("data/clearfeed_crawled_documents.md", "w") as file:
                file.write(result.markdown)

if __name__=="__main__":
    # Run the async main function
    asyncio.run(main(url = "https://docs.clearfeed.ai/clearfeed-help-center/answers/ai-agents"))
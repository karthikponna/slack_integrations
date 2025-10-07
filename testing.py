import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    # Create an instance of AsyncWebCrawler
    async with AsyncWebCrawler() as crawler:
        # Run the crawler on a URL
        result = await crawler.arun(url="https://crawl4ai.com")
        print(result)
        
        if result:
            with open("data/crawled_documents.md", "w") as file:
                file.write(result.markdown)

if __name__=="__main__":
    # Run the async main function
    asyncio.run(main())
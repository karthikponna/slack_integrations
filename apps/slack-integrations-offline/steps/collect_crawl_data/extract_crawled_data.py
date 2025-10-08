from loguru import logger
from typing_extensions import Annotated
from zenml import get_step_context, step

from crawl4ai import AsyncWebCrawler

@step
def extract_crawled_data(

):
    pass


async def async_crawl(url:str):

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        
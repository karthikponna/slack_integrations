import asyncio
import os

import psutil
from crawl4ai import AsyncWebCrawler, CacheMode


class Crawl4AICrawler:

    def __init__(self, max_concurrent_requests:int = 10)-> None:
        
        self.max_concurrent_requests = max_concurrent_requests

    def __call__(self,):
        
        try:
            loop = asyncio.get_event_loop()

        except RuntimeError:
            return asyncio.run()
        
        else:
            loop.run_until_complete()


    def __crawl_batch(self, )

    
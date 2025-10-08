from pathlib import Path

from loguru import logger
from zenml import pipeline


@pipeline
def collect_crawl_data():
    pass
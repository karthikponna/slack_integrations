from pathlib import Path

from loguru import logger
from zenml import pipeline

from steps.collect_urls.extract_urls_from_sitemap import extract_urls_from_sitemap
from steps.collect_crawl_data.extract_crawled_data import extract_crawled_data
from steps.infrastructure.save_documents_to_disk import save_documents_to_disk
from steps.infrastructure.upload_to_s3 import upload_to_s3

@pipeline
def collect_crawl_data(
    url_prefix: str, 
    data_dir: Path = Path(),
    to_s3: bool = False,
    max_workers:int = 10,
) -> None:

    crawled_data_dir = data_dir / "crawled"
    logger.info(f"Saving crawled data to {crawled_data_dir}")
    

    urls = extract_urls_from_sitemap(url_prefix = url_prefix)

    crawled_documents = extract_crawled_data(urls=urls, max_workers=max_workers)

    save_documents_to_disk(documents=crawled_documents, output_dir=crawled_data_dir)

    if to_s3:
        upload_to_s3(
        folder_path=str(crawled_data_dir),
        s3_prefix="slack_integrations/crawled",
        after="save_documents_to_disk"
        )


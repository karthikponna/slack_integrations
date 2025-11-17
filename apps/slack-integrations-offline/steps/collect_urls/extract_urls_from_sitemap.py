import os
import requests
from typing_extensions import Annotated
from xml.etree import ElementTree
from loguru import logger

from zenml import step
from zenml.steps import get_step_context


@step
def extract_urls_from_sitemap(url_prefix: str) -> Annotated[list[str], "urls_from_sitemap"]:

    """Extract URLs from a sitemap XML file.

    Args:
        url_prefix: Base URL prefix to construct the sitemap URL from.

    Returns:
        list[str]: List of URLs extracted from the sitemap.
    """
    sitemap_url = url_prefix.rstrip('/') + '/sitemap-pages.xml'
    logger.info(f"Constructed sitemap url {sitemap_url}")

    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()

        root = ElementTree.fromstring(response.content)

        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]

        logger.info(f"Successfully extracted no. of urls {len(urls)}")
        
        step_context = get_step_context()
        step_context.add_output_metadata(
            output_name="urls_from_sitemap",
            metadata={
                "len_of_urls": len(urls),
            }
        )

        return urls

    except Exception as e:
        logger.error(f"Error in extracting urls from sitemap {e}")
        logger.exception("Full traceback:")
        raise
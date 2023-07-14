from typing import List

from scrapy.crawler import CrawlerProcess

from raker.utils import validate_urls
from raker.spiders import get_spider_cls_by_url


class Raker:
    """
    Access raker functionality via this interface
    """
    RAKER_PROCESSOR = CrawlerProcess()

    @staticmethod
    def from_url(url, timeout=None):
        """
        Extract keywords from a URL
        :param url: URL to extract keywords from
        :param timeout: Timeout for the request
        :return: List of keywords
        """
        return Raker.from_urls([url], timeout=timeout)[url]

    @staticmethod
    def from_urls(urls: List[str], timeout=None):
        """
        Extract keywords from a list of URLs
        :param urls: List of URLs to extract keywords from
        :param timeout: Timeout for the request
        :return: Dictionary of keywords
        """
        if not validate_urls(urls):
            raise ValueError("Invalid URLs")

        spider_cls = get_spider_cls_by_url(urls[0])
        Raker.RAKER_PROCESSOR.crawl(spider_cls, urls=urls)
        Raker.RAKER_PROCESSOR.start()

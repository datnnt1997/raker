import os

from .youtube_spider import YouTubeCommentAPISpider, YouTubeCommentSeleniumSpider

from urllib.parse import urlparse


def get_spider_cls_by_url(url: str):
    """
    Get the raker.spider class for a given URL
    :param url: URL to get the spider class for
    :return: Spider class
    """
    domain = urlparse(url).netloc
    if 'youtube.com' in domain:
        return YouTubeCommentAPISpider if os.environ.get('YOUTUBE_API_KEY', None) else YouTubeCommentSeleniumSpider
    else:
        raise ValueError(f"Unsupported domain: {domain}")


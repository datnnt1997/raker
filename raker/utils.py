from typing import List
from urllib.parse import urlparse

import validators


def validate_urls(urls: List[str]):
    """
    Validate all string in list are url and have same domain
    :param urls: List of URLs to validate
    :return: Boolean
    """
    if len(urls) == 0:
        return False
    domain = urlparse(urls[0]).netloc
    for url in urls[1:]:
        if not validators.url(url):
            return False
        if not validators.domain(url) == domain:
            return False
    return True

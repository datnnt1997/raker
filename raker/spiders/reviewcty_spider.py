import scrapy
import logging


class ReviewCTySpider(scrapy.Spider):
    """ A spider to crawl ReviewCTy reviews. """

    name = 'ReviewCTySpider'
    task = 'ReviewCTyReview'
    start_urls = None
    custom_settings = {
        'ITEM_PIPELINES': {}
    }
    allowed_domains = ['googleapis.com', 'youtube.com']

    def __init__(self, urls, *args, **kwargs):
        super(ReviewCTySpider, self).__init__(*args, **kwargs)
        self._logger = logging.getLogger(__name__)

    def start_requests(self):
        yield scrapy.Request(url='https://reviewcty.net/', callback=self.parse)


def parse(self, response, **kwargs):
    pass
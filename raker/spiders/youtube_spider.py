from selenium import webdriver
from scrapy_selenium import SeleniumRequest

from webdriver_manager.chrome import ChromeDriverManager

import logging
import scrapy


class YouTubeSpider(scrapy.Spider):
    """
    A spider for scraping YouTube comments.
    """
    name = 'YouTubeSpider'

    start_urls = None

    custom_settings = {
        'SELENIUM_DRIVER_NAME': 'chrome',
        'SELENIUM_DRIVER_EXECUTABLE_PATH': ChromeDriverManager().install(),
        'SELENIUM_DRIVER_ARGUMENTS': ['-headless'],
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_selenium.SeleniumMiddleware': 800
        }
    }

    def __init__(self, urls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = logging.getLogger(__name__)
        self.start_urls = urls if isinstance(urls, list) else [urls]
        super(YouTubeSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        if not self.start_urls and hasattr(self, "start_url"):
            raise AttributeError(
                "Crawling could not start: 'start_urls' not found "
                "or empty (but found 'start_url' attribute instead, "
                "did you miss an 's'?)"
            )
        for url in self.start_urls:
            yield SeleniumRequest(url=url, callback=self.parse, wait_time=180, screenshot=True,
                                  script='window.scrollTo(0, document.body.scrollHeight);'
                                  )


    def parse(self, response, **kwargs):
        with open('image.png', 'wb') as image_file:
            image_file.write(response.meta['screenshot'])
        self._logger.info(f'Parsing {response}')
        self._logger.info(response.selector.xpath('//title/@text'))

    @staticmethod
    def close(spider, reason):
        closed = getattr(spider, "closed", None)
        if callable(closed):
            return closed(reason)


if __name__ == '__main__':
    """
    Debugging code for the YoutubeSpider class.
    """
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess()
    process.crawl(YouTubeSpider, urls=['https://www.youtube.com/watch?v=9bZkp7q19f0'])
    process.start()

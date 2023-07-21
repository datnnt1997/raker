import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from scrapy_selenium import SeleniumRequest

from webdriver_manager.chrome import ChromeDriverManager

from raker.items.youtube_items import YouTubeComment

import logging
import scrapy
import json


class YouTubeCommentSpider(scrapy.Spider):
    """ A base spider for scraping YouTube comments."""
    name = 'YTCommentSpider'
    task = 'YTubeComment'
    start_urls = None
    custom_settings = {'ITEM_PIPELINES': {
        'raker.pipelines.youtube_pipeline.YouTubeNomalizePipeline': 600,
        'raker.pipelines.youtube_pipeline.YouTubeDuplicatesPipeline.': 700,
    }}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = logging.getLogger(__name__)
        super(YouTubeCommentSpider, self).__init__(*args, **kwargs)

    @classmethod
    def update_settings(cls, settings):
        if os.environ.get('MONGO_URI', None):
            cls.custom_settings['ITEM_PIPELINES']['raker.pipelines.mongodb_pipeline.MongoPipeline'] = 800
        else:
            cls.custom_settings['ITEM_PIPELINES']['raker.pipelines.youtube_pipeline.YouTubeJsonWriterPipeline'] = 800
        settings.setdict(cls.custom_settings or {}, priority='spider')


class YouTubeCommentAPISpider(YouTubeCommentSpider):
    """ A spider for scraping YouTube comments using the YouTube Data API v3."""
    name = 'YTCommentAPISpider'
    api_domain = 'https://www.googleapis.com/youtube/v3'
    allowed_domains = ['googleapis.com', 'youtube.com']

    def __init__(self, urls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_key = os.environ.get('YOUTUBE_API_KEY', None)
        if not self._api_key:
            raise ValueError("No YouTube API key provided.")
        self.start_urls = [self._build_api_url(url) for url in urls] if isinstance(urls, list) else [
            self._build_api_url(urls)]
        super(YouTubeCommentAPISpider, self).__init__(*args, **kwargs)

    @staticmethod
    def _get_video_id(url):
        """Extracts the video ID from a YouTube URL."""
        queries: dict = parse_qs(urlparse(url).query)
        if 'v' in queries:
            return queries['v'][0]
        elif 'videoId' in queries:
            return queries['videoId'][0]

    @staticmethod
    def _get_channel_id(url):
        """Extracts the channel ID from a YouTube URL."""
        return url.split('/')[-1]

    @staticmethod
    def update_page_token(url, new_page_token):
        parsed_url = urlparse(url)
        query_params: dict = parse_qs(parsed_url.query)

        if 'pageToken' in query_params:
            query_params['pageToken'] = new_page_token
        else:
            query_params['pageToken'] = [new_page_token]

        updated_query = urlencode(query_params, doseq=True)
        updated_url = urlunparse(parsed_url._replace(query=updated_query))

        return updated_url

    def _build_api_url(self, request_url, page_token=None):
        """Converts a regular YouTube URL to a YouTube Data API URL."""
        if 'youtube.com/watch' in request_url:
            video_id = self._get_video_id(request_url)
            url = f'{self.api_domain}/commentThreads?part=snippet,replies,id&textFormat=plainText&videoId={video_id}' \
                  f'&maxResults=100&key={self._api_key}'
        elif 'youtube.com/channel' in request_url:
            channel_id = self._get_channel_id(request_url)
            url = f'{self.api_domain}/commentThreads?part=snippet,replies,id&textFormat=plainText' \
                  f'&allThreadsRelatedToChannelId={channel_id}' \
                  f'&maxResults=100&key={self._api_key}'
        elif 'youtube.com/@' in request_url or 'googleapis.com/youtube/v3' in request_url:
            url = request_url
        else:
            raise ValueError(f'Unsupported URL: {request_url}')
        if page_token:
            url = self.update_page_token(url, page_token)
        return url

    def start_requests(self):
        if not self.start_urls and hasattr(self, "start_url"):
            raise AttributeError(
                "Crawling could not start: 'start_urls' not found "
                "or empty (but found 'start_url' attribute instead, "
                "did you miss an 's'?)"
            )
        for url in self.start_urls:
            if 'youtube.com' in url:
                yield scrapy.Request(method='GET', url=url, callback=self.parse_channel)
            else:
                yield scrapy.Request(method='GET', url=url, callback=self.parse)

    def parse_channel(self, response, **kwargs):
        # Extract channel url from response
        channel_url = response.xpath('/html/body/link[1]/@href').get()
        # Build API url for channel url
        api_url = self._build_api_url(channel_url)
        yield scrapy.Request(method='GET', url=api_url, callback=self.parse)

    def parse(self, response, **kwargs):
        data = json.loads(response.body)
        self._logger.info(data)
        for item in data['items']:
            yield YouTubeComment(
                _id=item['id'],
                author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                content=item['snippet']['topLevelComment']['snippet']['textOriginal'],
                video_id=item['snippet']['videoId'],
                like_count=item['snippet']['topLevelComment']['snippet']['likeCount'],
                reply_count=item['snippet']['totalReplyCount'])
            if 'replies' not in item:
                continue
            for reply in item['replies']['comments']:
                yield YouTubeComment(
                    _id=reply['id'],
                    author=reply['snippet']['authorDisplayName'],
                    content=reply['snippet']['textOriginal'],
                    video_id=item['snippet']['videoId'],
                    like_count=reply['snippet']['likeCount'])
        # Get the next page token and recursively call this method
        if 'nextPageToken' in data:
            next_page_token = data['nextPageToken']
            next_page_url = self._build_api_url(response.url, next_page_token)
            yield scrapy.Request(method='GET', url=next_page_url, callback=self.parse)


class YouTubeCommentSeleniumSpider(YouTubeCommentSpider):
    """ A spider for scraping YouTube comments."""
    name = 'YTCommentSeleniumSpider'
    allowed_domains = ['www.youtube.com']

    custom_settings = {
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'SELENIUM_DRIVER_NAME': 'chrome',
        'SELENIUM_DRIVER_EXECUTABLE_PATH': ChromeDriverManager().install(),
        'SELENIUM_DRIVER_ARGUMENTS': [],
        'DOWNLOADER_MIDDLEWARES': {
            'raker.middlewares.YouTubeMiddleware': 800
        }
    }

    def __init__(self, urls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = urls if isinstance(urls, list) else [urls]
        super(YouTubeCommentSeleniumSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        if not self.start_urls and hasattr(self, "start_url"):
            raise AttributeError("No start URLs provided. Please provide URLs for the spider to crawl.")
        for url in self.start_urls:
            yield SeleniumRequest(url=url,
                                  callback=self.parse,
                                  wait_time=180,
                                  screenshot=True,
                                  script='window.scrollTo(0, document.body.scrollHeight);')

    def parse(self, response, **kwargs):
        with open('image.png', 'wb') as image_file:
            image_file.write(response.meta['screenshot'])
        comments = response.xpath('//*[@id="comment"]')
        self._logger.info(f'Found {len(comments)} comments.')

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

    os.environ['YOUTUBE_API_KEY'] = ''
    process = CrawlerProcess()
    process.crawl(YouTubeCommentAPISpider,
                  urls=['https://www.youtube.com/@enjoylifeandloveyourself'])
    process.start()

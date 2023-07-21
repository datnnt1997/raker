from raker.items import ReviewCTyReview
from scrapy.loader import ItemLoader

import os
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
    allowed_domains = ['reviewcty.net']

    def __init__(self, urls, *args, **kwargs):
        super(ReviewCTySpider, self).__init__(*args, **kwargs)
        self._logger = logging.getLogger(__name__)
        self.start_urls = urls if isinstance(urls, list) else [urls]

    def start_requests(self):
        if not self.start_urls and not self.start_urls[0]:
            raise AttributeError("No start URLs provided. Please provide URLs for the spider to crawl.")
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    @staticmethod
    def _parse_card_review(rcard: scrapy.Selector) -> ReviewCTyReview:
        """ Parse a review card to extract the review's information. """
        print(rcard)
        review = ItemLoader(item=ReviewCTyReview(), selector=rcard)
        review.add_xpath('content', './/div[contains(@class, "card-body")]/p[contains(@class, "text-content")]/text()')
        review.add_value('_id', rcard.attrib['id'])
        review.add_xpath('author', './/div[contains(@class, "card-header")]/p[@class="star-rv"]/text()[1]')
        review.add_value('company_id', rcard.attrib['data-companyid'])
        review.add_xpath('like_count', './/span[@data-reaction="1"]/text()')
        review.add_xpath('dislike_count', './/span[@data-reaction="2"]/text()')
        return review.load_item()

    @staticmethod
    def _parse_reply(reply: scrapy.Selector, reply_id: str, company_id: str) -> ReviewCTyReview:
        """ Parse a reply card to extract the reply's information. """
        review = ItemLoader(item=ReviewCTyReview(), selector=reply)
        review.add_xpath('content', './/p[contains(@class, "text-content")]/text()')
        review.add_value('_id', reply_id)
        review.add_xpath('author', './/p[contains(@class, "comment__title")]/span[@class="has-text-weight-bold"]/text()[1]')
        review.add_value('company_id', company_id)
        review.add_value('like_count', 0)
        review.add_value('dislike_count', 0)
        review.add_value('reply_count', 0)
        review.load_item()
        pass
    def parse(self, response, **kwargs):
        # Get the review cards
        for review_card in response.xpath('//div[contains(@class, "card-rv")]'):
            review = self._parse_card_review(review_card)
            replies = review_card.xpath('.//div[@class="review-comments"]/div[@class="comment"]')
            review.reply_count = len(replies)
            yield review
            for r_idx, reply in enumerate(replies):
                yield self._parse_reply(reply, reply_id=f"{review._id}_{r_idx}", company_id=review.company_id)


if __name__ == '__main__':
    """
    Debugging code for the ReviewCTySpider class.
    """
    from scrapy.crawler import CrawlerProcess

    os.environ['YOUTUBE_API_KEY'] = ''
    process = CrawlerProcess()
    process.crawl(ReviewCTySpider,
                  urls=['https://reviewcty.net/company/saokim-branding?page=1'])
    process.start()

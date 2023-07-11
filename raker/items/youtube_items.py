from scrapy import Item


class YouTubeComment(Item):
    author: str
    content: str
    published_at: str
    updated_at: str
    like_count: int
    dislike_count: int

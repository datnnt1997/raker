from typing import Optional
from dataclasses import dataclass, field
from itemloaders.processors import Join, MapCompose

import scrapy


@dataclass
class ReviewCTyReview(scrapy.Item):
    content: str = scrapy.Field(input_processor=MapCompose(str.strip))
    _id: str = field(default=None)
    author: Optional[str] = field(default=None)
    company_id: Optional[str] = field(default=None)
    like_count: Optional[int] = field(default=None)
    dislike_count: Optional[int] = field(default=None)
    reply_count: Optional[int] = field(default=None)
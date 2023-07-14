import os

import pymongo
from itemadapter import ItemAdapter


class MongoPipeline:
    collection_name = "scrapy_items"

    def __init__(self, mongo_uri, mongo_db):
        self._client = None
        self._db = None
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        cls.collection_name = os.environ.get('MONGO_COLLECTION', crawler.spider.task )
        return cls(
            mongo_uri=os.environ.get('MONGO_URI'),
            mongo_db=os.environ.get('MONGO_DATABASE'),
        )

    def open_spider(self, spider):
        self._client = pymongo.MongoClient(self.mongo_uri)
        self._db = self._client[self.mongo_db]

    def close_spider(self, spider):
        self._client.close()

    def process_item(self, item, spider):
        self._db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item

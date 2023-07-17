from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class DuplicatesPipeline:
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter["_id"] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item['_id']}")
        else:
            self.ids_seen.add(adapter["_id"])
            return item


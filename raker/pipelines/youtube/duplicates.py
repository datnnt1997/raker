from itemadapter import ItemAdapter

from scrapy.exceptions import DropItem

from raker.pipelines.duplicates_pipeline import DuplicatesPipeline
from raker.pipelines.json_pipeline import JsonWriterPipeline

import json
import re


class YouTubeJsonWriterPipeline(JsonWriterPipeline):
    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self._file.write(line)
        return item





class YouTubeDuplicatesPipeline(DuplicatesPipeline):
    def __init__(self):
        super().__init__()
        self.contents = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter["_id"] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item['_id']}")
        elif adapter["content"] in self.contents:
            raise DropItem(f"Duplicate item found: {item['content']}")
        else:
            self.ids_seen.add(adapter["_id"])
            self.contents.add(adapter["content"])
            return item

from itemadapter import ItemAdapter

from .json_pipeline import JsonWriterPipeline

import json


class YouTubeJsonWriterPipeline(JsonWriterPipeline):
    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self._file.write(line)
        return item

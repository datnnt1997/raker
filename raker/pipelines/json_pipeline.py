from itemadapter import ItemAdapter

import os
import json
import datetime


class JsonWriterPipeline(object):

    def __init__(self, fpath):
        self._file = None
        self.fpath = fpath

    @classmethod
    def from_crawler(cls, crawler):
        fpath = crawler.settings.get('OUTPUT_FILE',
                                     f'results/{crawler.spider.task}_'
                                     f'{datetime.datetime.now().strftime("%d%b%y_%I%p%M%S")}.jsonl')
        dir_path = os.path.dirname(fpath)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return cls(fpath=fpath)

    def open_spider(self, spider):
        self._file = open(self.fpath, "w", encoding="utf-8")

    def close_spider(self, spider):
        self._file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self._file.write(line)
        return item

from scrapy.exceptions import DropItem

import re

class YouTubeNomalizePipeline:
    def process_item(self, item, spider):
        content = item.content
        # Remove \xa0 (non-breaking space) and \u200b (zero-width space) characters
        content = re.sub("[\xa0\u200b]", " ", content)
        # Remove multiple spaces, tabs, and newlines
        content = re.sub("\n+", "\n", content)
        content = re.sub("\t+", "\t", content)
        content = re.sub(" +", " ", content)
        # Remove leading and trailing spaces, tabs, and newlines
        content = content.strip()
        if not item.content or len(item.content) == 0:
            raise DropItem(f"Empty item found: {item['content']}")
        item.content = content
        return item

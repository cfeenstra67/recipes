import base64
import json
import logging

import scrapy

from scraping.items import RecipeItem


LOGGER = logging.getLogger(__name__)


class RecipePipeline:
    """
    """
    @classmethod
    def from_crawler(cls, crawler: scrapy.crawler.Crawler) -> "RecipePipeline":
        return cls(
            crawler.settings["JSON_OUTPUT_FILE"],
            crawler.settings["OVERWRITE_OUTPUT_FILES"]
        )

    def __init__(self, output_file: str, overwrite: bool) -> None:
        self.output_file = output_file
        self.stream = None
        self.overwrite = overwrite

    def process_item(self, item: RecipeItem, spider: scrapy.Spider) -> scrapy.Item:
        json_data = dict(item)
        encoded_html = base64.b64encode(item["html"]).decode()
        json_data["html"] = encoded_html
        self.stream.write(json.dumps(json_data) + "\n")
        LOGGER.info("Processed %s", item["url"])
        return item

    def open_spider(self, spider: scrapy.Spider) -> None:
        mode = "w+" if self.overwrite else "a+"
        self.stream = open(self.output_file, mode)

    def close_spider(self, spider: scrapy.Spider) -> None:
        self.stream.close()
        self.stream = None

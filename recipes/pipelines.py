import hashlib
import json
import logging
import os
import shutil

from fs import open_fs
import scrapy

from recipes.items import RecipeItem


LOGGER = logging.getLogger(__name__)


class RecipePipeline:
    """ """

    @classmethod
    def from_crawler(cls, crawler: scrapy.crawler.Crawler) -> "RecipePipeline":
        return cls(crawler.settings["RECIPES_OUTPUT_URI"])

    def __init__(self, output_uri: str) -> None:
        self.output_uri = output_uri
        self.filesystem = None

    def process_item(
        self, item: RecipeItem, spider: scrapy.Spider  # pylint: disable=unused-argument
    ) -> scrapy.Item:
        json_data = dict(item)
        html_data = json_data.pop("html")

        url_hash = hashlib.sha1(item["url"].encode()).hexdigest()

        if not self.filesystem.isdir(url_hash):
            self.filesystem.makedirs(url_hash)

        with self.filesystem.open(os.path.join(url_hash, "page.html"), "wb+") as file:
            file.write(html_data)

        with self.filesystem.open(
            os.path.join(url_hash, "meta.json"), "w+", encoding="utf-8"
        ) as file:
            json.dump(json_data, file, indent=2, sort_keys=True)

        LOGGER.info("Processed %s", item["url"])
        return item

    def open_spider(
        self, spider: scrapy.Spider  # pylint: disable=unused-argument
    ) -> None:
        LOGGER.info("Opened spider: %s; writing to %s", spider.name, self.output_uri)
        self.filesystem = open_fs(self.output_uri, create=True)

    def close_spider(  # pylint: disable=no-self-use
        self, spider: scrapy.Spider  # pylint: disable=unused-argument
    ) -> None:
        LOGGER.info("Closed spider: %s", spider.name)
        self.filesystem.close()
        self.filesystem = None

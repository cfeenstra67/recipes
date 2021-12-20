import json
import logging
import os
from datetime import datetime
from urllib.parse import urlencode

from fs import open_fs
from scrapy import signals


LOGGER = logging.getLogger(__name__)


class RecipeErrorHandlerMiddleware:
    """
    Write error info to a file
    """

    def __init__(self, output_uri: str) -> None:
        self.errors = {}
        self.filesystems = {}
        self.last_lines = {}
        self.output_uri = output_uri

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        instance = cls(crawler.settings["RECIPES_ERRORS_OUTPUT_URI"])
        crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(instance.spider_closed, signal=signals.spider_closed)
        return instance

    def process_spider_exception(
        self, response, exception, spider
    ):  # pylint: disable=unused-argument
        if spider.name not in self.errors:
            LOGGER.error("output stream for %s not found.", spider.name)
            return

        obj = {
            "url": response.url,
            "error_type": type(exception).__name__,
            "error": str(exception),
            "timestamp": int(datetime.utcnow().timestamp()),
        }

        line = json.dumps(obj) + "\n"
        if self.last_lines.get(spider.name) == line:
            return
        self.errors[spider.name].write(line)
        self.last_lines[spider.name] = line

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s", spider.name)
        dirname, filename = os.path.split(self.output_uri)
        fs = self.filesystems[spider.name] = open_fs(dirname, create=True)
        self.errors[spider.name] = fs.open(filename, "a+")

    def spider_closed(self, spider):
        spider.logger.info("Spider closed: %s", spider.name)
        self.last_lines.pop(spider.name, None)

        if spider.name in self.errors:
            error_stream = self.errors.pop(spider.name)
            error_stream.close()

        if spider.name in self.filesystems:
            fs = self.filesystems.pop(spider.name)
            fs.close()



class ScraperApiProxy:
    """
    Proxy requests through scraper API
    """
    def __init__(self, enabled: bool, api_key: str) -> None:
        self.enabled = enabled
        self.api_key = api_key

    @classmethod
    def from_crawler(cls, crawler) -> "ScraperApiProxy":
        return cls(
            crawler.settings["SCRAPER_API_ENABLED"],
            crawler.settings["SCRAPER_API_KEY"]
        )

    def process_request(self, request, spider):
        if not self.enabled:
            return

        params = urlencode({
            "api_key": self.api_key,
            "url": request.url
        })
        new_url = f"https://api.scraperapi.com?{params}"

        return request.replace(url=new_url)

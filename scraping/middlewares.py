# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging

from scrapy import signals


LOGGER = logging.getLogger(__name__)


class RecipeErrorHandlerMiddleware:
    """
    Write error URLs to a file
    """

    def __init__(self, output_file: str, overwrite: bool) -> None:
        self.errors = {}
        self.last_lines = {}
        self.output_file = output_file
        self.overwrite = overwrite

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        instance = cls(
            crawler.settings["ERRORS_OUTPUT_FILE"],
            crawler.settings["OVERWRITE_OUTPUT_FILES"],
        )
        crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(instance.spider_closed, signal=signals.spider_closed)
        return instance

    def process_spider_exception(
        self, response, exception, spider
    ):  # pylint: disable=unused-argument
        if spider.name not in self.errors:
            LOGGER.error("output stream for %s not found.", spider.name)
            return
        line = response.url + "\n"
        if self.last_lines.get(spider.name) == line:
            return
        self.errors[spider.name].write(response.url + "\n")
        self.last_lines[spider.name] = line

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s", spider.name)
        mode = "w+" if self.overwrite else "a+"
        self.errors[spider.name] = open(self.output_file, mode, encoding="utf-8")

    def spider_closed(self, spider):
        spider.logger.info("Spider closed: %s", spider.name)
        self.last_lines.pop(spider.name, None)
        if spider.name not in self.errors:
            return
        error_stream = self.errors.pop(spider.name)
        error_stream.close()

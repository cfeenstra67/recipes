import logging
import re
from typing import Iterator
from urllib.parse import urljoin, urlparse

import scrapy
from lxml import html

from scraping.site_listers.base import PageCallback, SiteLister


LOGGER = logging.getLogger(__name__)


class ArchanasKitchenLister(SiteLister):
    """ """

    start_url = "https://www.archanaskitchen.com/recipes"

    page_url_regex = re.compile(r"^/recipes/page-(\d+)$")

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:
        def parse_single_list_page(response):
            html_data = html.fromstring(response.body)

            blog_links = html_data.cssselect("div.blogRecipe > div > a")
            for link in blog_links:
                absolute_link = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(absolute_link, callback=page_callback)

        def parse_first_list_page(response):

            html_data = html.fromstring(response.body)

            end_link = html_data.find('.//div[@class="pagination"]//a[@title="End"]')
            if end_link is None:
                LOGGER.error("Unable to find last page.")
                yield from parse_single_list_page(response)
                return

            parsed_link = urlparse(end_link.attrib["href"])
            match = self.page_url_regex.search(parsed_link.path)
            if not match:
                LOGGER.error(
                    "No match found for page number in path: %s", parsed_link.path
                )
                yield from parse_single_list_page(response)
                return

            last_page = int(match.group(1))

            LOGGER.info("Last page: %d", last_page)

            for page_num in range(2, last_page + 1):
                yield scrapy.Request(
                    f"{self.start_url}/page-{page_num}",
                    callback=parse_single_list_page,
                    dont_filter=True,
                )

            yield from parse_single_list_page(response)

        yield scrapy.Request(
            self.start_url, callback=parse_first_list_page, dont_filter=True
        )

import logging
import re
from typing import Iterator
from urllib.parse import urljoin, urlparse

import scrapy
from lxml import html

from scraping.site_listers.base import PageCallback, SiteLister


LOGGER = logging.getLogger(__name__)


class BudgetBytesLister(SiteLister):
    """
    """
    start_url = "https://www.budgetbytes.com/category/recipes/"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        def parse_single_list_page(response):
            html_data = html.fromstring(response.body)
            for link in html_data.cssselect("div#content > article.post a"):
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(url, callback=page_callback)

        def parse_first_list_page(response):
            html_data = html.fromstring(response.body)
            page_nums = html_data.cssselect("div.nav-links > a.page-numbers")
            pages = []
            for element in page_nums:
                try:
                    pages.append(int(element.text))
                except ValueError:
                    pass

            if not pages:
                LOGGER.error("No page numbers found.")
            else:
                LOGGER.info("Last page: %d", pages[-1])
                for page_num in range(2, pages[-1] + 1):
                    yield scrapy.Request(
                        f"{self.start_url}page/{page_num}",
                        callback=parse_single_list_page,
                        dont_filter=True
                    )

            yield from parse_single_list_page(response)

        yield scrapy.Request(self.start_url, callback=parse_first_list_page, dont_filter=True)

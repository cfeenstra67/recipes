import logging
from typing import Iterator
from urllib.parse import urljoin

import scrapy
from lxml import html

from scraping.site_listers.base import PageCallback, SiteLister


LOGGER = logging.getLogger(__name__)


class BBCLister(SiteLister):
    """ """

    start_url = "https://www.bbc.co.uk/food/recipes/a-z"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:
        def parse_single_list_page(response):
            html_data = html.fromstring(response.body)
            for link in html_data.cssselect("div.promo-collection > div > a.promo"):
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(url, callback=page_callback)

        def parse_first_list_page(response, letter):
            html_data = html.fromstring(response.body)
            page_nums = html_data.cssselect("div.pagination > ul > li > a")
            pages = []
            for element in page_nums:
                try:
                    pages.append(int(element.text))
                except (ValueError, TypeError):
                    pass

            if not pages:
                LOGGER.error("No page numbers found.")
            else:
                LOGGER.info("Last page: %d", pages[-1])
                for page_num in range(2, pages[-1] + 1):
                    yield scrapy.Request(
                        f"{self.start_url}/{letter}/{page_num}",
                        callback=parse_single_list_page,
                        dont_filter=True,
                    )

            yield from parse_single_list_page(response)

        letters = list(map(lambda x: chr(ord("a") + x), range(26)))
        letters.append("0-9")

        for letter in letters:
            yield scrapy.Request(
                f"{self.start_url}/{letter}",
                callback=parse_first_list_page,
                cb_kwargs={"letter": letter},
                dont_filter=True,
            )

import logging
from typing import Iterator
from urllib.parse import urljoin

import scrapy
from lxml import html

from recipes.site_listers.base import PageCallback, SiteLister


LOGGER = logging.getLogger(__name__)


class CastIronKetoLister(SiteLister):
    """ """

    start_url = "https://www.castironketo.net/blog/category/recipe/"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:
        def parse_single_list_page(response):
            html_data = html.fromstring(response.body)
            for link in html_data.cssselect("main.content > article.post a"):
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(url, callback=page_callback)

        def parse_first_list_page(response):
            html_data = html.fromstring(response.body)
            page_nums = html_data.cssselect("div.pagination > ul > li > a")
            pages = []
            for element in page_nums:
                try:
                    pages.append(int(element[0].tail.strip()))
                except (ValueError, TypeError, IndexError, AttributeError):
                    pass

            if not pages:
                LOGGER.error("No page numbers found.")
            else:
                LOGGER.info("Last page: %d", pages[-1])
                for page_num in range(2, pages[-1] + 1):
                    yield scrapy.Request(
                        f"{self.start_url}page/{page_num}",
                        callback=parse_single_list_page,
                        dont_filter=True,
                    )

            yield from parse_single_list_page(response)

        yield scrapy.Request(
            self.start_url, callback=parse_first_list_page, dont_filter=True
        )

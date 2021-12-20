import logging
from typing import Iterator
from urllib.parse import urljoin

import scrapy
from lxml import html

from recipes.site_listers.base import PageCallback, SiteLister


LOGGER = logging.getLogger(__name__)


class FoodNetworkLister(SiteLister):
    """ """

    start_url = "https://www.foodnetwork.com/recipes/recipes-a-z"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        first_letter = "123"

        def parse_single_list_page(response):
            html_data = html.fromstring(response.body)
            for link in html_data.cssselect(
                "div.o-Capsule__m-Body > div > ul > li > a"
            ):
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(url, callback=page_callback)

        def parse_letter_first_list_page(response, letter):
            html_data = html.fromstring(response.body)
            pages = []
            for element in html_data.cssselect("section.o-Pagination > ul > li > a"):
                try:
                    pages.append(int(element.text))
                except (ValueError, TypeError):
                    pass

            if pages:
                for page_num in range(2, pages[-1]):
                    new_url = f"{response.url}/p/{page_num}"
                    yield scrapy.Request(
                        new_url, callback=parse_single_list_page, dont_filter=True
                    )
            else:
                LOGGER.error("No pages found for letter: %s", letter)

            yield from parse_single_list_page(response)

        def parse_first_list_page(response):
            html_data = html.fromstring(response.body)
            letter_sections = html_data.cssselect(
                "section.o-IndexPagination > ul > li > a"
            )
            for link in letter_sections:
                # This is the first page
                if link.text == first_letter:
                    continue
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(
                    url,
                    callback=parse_letter_first_list_page,
                    dont_filter=True,
                    cb_kwargs={"letter": link.text},
                )

            yield from parse_letter_first_list_page(response, first_letter)

        yield scrapy.Request(
            self.start_url, callback=parse_first_list_page, dont_filter=True
        )

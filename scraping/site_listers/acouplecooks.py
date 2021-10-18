import logging
from typing import Iterator
from urllib.parse import urljoin

import scrapy
from lxml import html

from scraping.site_listers.base import PageCallback, SiteLister


LOGGER = logging.getLogger(__name__)


class ACoupleCooksLister(SiteLister):
    """
    """
    start_url = "https://www.acouplecooks.com/category/recipes/"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        def handle_list_page(response: scrapy.http.Response, page: int = 1):
            if response.status == 404:
                LOGGER.info("Page %d does not exist, exiting", page)
                return

            next_page = page + 1
            yield scrapy.Request(
                f"{self.start_url}?_paged={next_page}",
                callback=handle_list_page,
                cb_kwargs={"page": next_page},
                dont_filter=True
            )

            html_data = html.fromstring(response.body)
            for post in html_data.cssselect(
                "div.archive-post-listing > article.post-summary"
            ):
                link = post.cssselect("a")[0].attrib["href"]
                absolute_link = urljoin(response.url, link)
                yield scrapy.Request(link, callback=page_callback)

        yield scrapy.Request(self.start_url, callback=handle_list_page, dont_filter=True)

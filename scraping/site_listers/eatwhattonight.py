from typing import Iterator
from urllib.parse import urljoin

import scrapy
from lxml import html

from scraping.site_listers.base import PageCallback, SiteLister


class EatWhatTonightLister(SiteLister):
    """ """

    start_url = "https://eatwhattonight.com/recipe-index-by-list/"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:
        def handle_list_page(response):
            html_data = html.fromstring(response.body)
            for link in html_data.cssselect(
                "section.content-area > ul.recipe_index_list_posts > li > h3 > a"
            ):
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(url, callback=page_callback)

        yield scrapy.Request(
            self.start_url, callback=handle_list_page, dont_filter=True
        )

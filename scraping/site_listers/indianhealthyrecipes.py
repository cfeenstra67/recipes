from typing import Iterator
from urllib.parse import urljoin

import scrapy
from lxml import html

from scraping.site_listers.base import SiteLister, PageCallback


class IndianHealthyRecipesLister(SiteLister):
    """ """

    start_url = "https://www.indianhealthyrecipes.com/recipes/"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:
        def process_page(response):
            html_data = html.fromstring(response.body)
            links = html_data.cssselect(".pt-cv-page .pt-cv-gls-content h4 > a")
            for link in links:
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(url, callback=page_callback)

        yield scrapy.Request(self.start_url, callback=process_page, dont_filter=True)

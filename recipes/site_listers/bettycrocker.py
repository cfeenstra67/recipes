import logging
from typing import Iterator
from urllib.parse import urljoin

import scrapy
from lxml import etree

from recipes.site_listers.base import PageCallback, SiteLister


LOGGER = logging.getLogger(__name__)


class BettyCrockerLister(SiteLister):
    """ """

    start_url = "https://www.bettycrocker.com/recipe.xml"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        def parse_sitemap(response: scrapy.http.Response):
            tree = etree.fromstring(response.body)
            for location in tree.findall(".//sm:url/sm:loc", namespaces=namespaces):
                yield scrapy.Request(
                    urljoin(response.url, location.text),
                    callback=page_callback,
                    dont_filter=True,
                )

        yield scrapy.Request(self.start_url, callback=parse_sitemap, dont_filter=True)

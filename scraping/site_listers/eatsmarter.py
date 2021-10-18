import logging
import re
from typing import Iterator
from urllib.parse import urljoin, urlparse

import scrapy
from lxml import etree

from scraping.site_listers.base import PageCallback, SiteLister


LOGGER = logging.getLogger(__name__)


class EatSmarterLister(SiteLister):
    """ """

    start_url = "https://eatsmarter.com/sitemap.xml"

    recipe_url_regex = re.compile(r"^/recipes/[^/]+$")

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        def parse_individual_sitemap(response: scrapy.http.Response):
            tree = etree.fromstring(response.body)
            for location in tree.findall(".//sm:url/sm:loc", namespaces=namespaces):
                url = urljoin(response.url, location.text)
                parsed_url = urlparse(url)
                if not self.recipe_url_regex.search(parsed_url.path):
                    continue
                yield scrapy.Request(url, callback=page_callback)

        def parse_sitemap(response: scrapy.http.Response):
            tree = etree.fromstring(response.body)
            for location in tree.findall(".//sm:sitemap/sm:loc", namespaces=namespaces):
                yield scrapy.Request(
                    urljoin(response.url, location.text),
                    callback=parse_individual_sitemap,
                    dont_filter=True,
                )

        yield scrapy.Request(self.start_url, callback=parse_sitemap, dont_filter=True)

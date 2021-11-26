from typing import Iterator
from urllib.parse import urljoin

import scrapy
from lxml import etree

from scraping.site_listers.base import PageCallback, SiteLister


class GonnaWantSecondsLister(SiteLister):
    """ """

    start_url = "https://www.gonnawantseconds.com/post-sitemap.xml"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        def parse_sitemap(response: scrapy.http.Response):
            tree = etree.fromstring(response.body)
            for location in tree.findall(".//sm:url/sm:loc", namespaces=namespaces):
                url = urljoin(response.url, location.text)
                yield scrapy.Request(url, callback=page_callback)

        yield scrapy.Request(self.start_url, callback=parse_sitemap, dont_filter=True)

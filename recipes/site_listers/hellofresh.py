import os
from typing import Iterator
from urllib.parse import urljoin

import scrapy
from lxml import etree

from recipes import DATA_DIR
from recipes.site_listers.base import PageCallback, SiteLister


class HelloFreshLister(SiteLister):
    """ """

    start_url = "https://www.hellofresh.com/sitemap_recipe_pages.xml"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        # Manually downloaded from `start_url`
        # in order to avoid cloudflare protection
        with open(
            os.path.join(DATA_DIR, "hellofresh_recipe_sitemap.xml"), "rb"
        ) as file:
            tree = etree.fromstring(file.read())
            for location in tree.findall(".//sm:url/sm:loc", namespaces=namespaces):
                url = urljoin(self.start_url, location.text)
                yield scrapy.Request(url, callback=page_callback, dont_filter=True)

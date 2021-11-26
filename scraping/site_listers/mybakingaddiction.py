import re
from typing import Sequence, Iterator
from urllib.parse import urljoin, urlparse

import scrapy
from lxml import etree

from scraping.site_listers.base import PageCallback, SitemapLister


class MyBakingAddictionLister(SitemapLister):
    """ """

    start_url = "https://www.mybakingaddiction.com/sitemap.xml"
    sitemap_path_regex = re.compile(r"^/sitemap-pt-post-\d+-\d+\.xml$")

    def process_start_urls(
        self, urls: Sequence[str], callback: PageCallback
    ) -> Iterator[scrapy.Request]:
        def get_sitemaps(response):
            tree = etree.fromstring(response.body)
            for relative_url in self.get_sitemap_urls(tree):
                url = urljoin(response.url, relative_url)
                parsed_url = urlparse(url)
                if not self.sitemap_path_regex.search(parsed_url.path):
                    continue
                yield scrapy.Request(url, callback=callback, dont_filter=True)

        yield from super().process_start_urls(urls, get_sitemaps)

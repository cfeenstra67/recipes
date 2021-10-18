import logging
import re
from typing import Sequence
from urllib.parse import urljoin, urlparse

import scrapy
from lxml import html

from scraping.site_listers.base import PageCallback, StructuredSiteLister


LOGGER = logging.getLogger(__name__)


class CookieAndKateLister(StructuredSiteLister):
    """
    """
    start_url = "https://cookieandkate.com/category/food-recipes/"

    def get_links(self, dom: html.Element) -> Sequence[str]:
        return [
            element.attrib["href"] for element in dom.cssselect(
                "main.content > div.lcp_catlist > div.lcp_catlist_item > a"
            )
        ]

    def get_pages(self, dom: html.Element, page: int) -> Sequence[int]:
        if not self.get_links(dom):
            return []
        return [page + 1]

    def get_page_url(self, page: int) -> str:
        return f"{self.start_url}page/{page}"
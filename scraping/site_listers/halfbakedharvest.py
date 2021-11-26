import logging
from typing import Sequence

from lxml import html

from scraping.site_listers.base import StructuredSiteLister


LOGGER = logging.getLogger(__name__)


class HalfBakedHarvestLister(StructuredSiteLister):
    """ """

    start_url = "https://www.halfbakedharvest.com/recipes/"

    def get_links(self, dom: html.Element) -> Sequence[str]:
        return [
            element.attrib["href"]
            for element in dom.cssselect("div.results > article.post-summary > div > a")
        ]

    def get_pages(self, dom: html.Element, page: int) -> Sequence[int]:
        if not self.get_links(dom):
            return []
        return [page + 1]

    def get_page_url(self, page: int) -> str:
        return f"{self.start_url}?_paged={page}"

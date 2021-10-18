import logging
from typing import Sequence

from lxml import html

from scraping.site_listers.base import StructuredSiteLister


LOGGER = logging.getLogger(__name__)


class CookStrLister(StructuredSiteLister):
    """ """

    start_url = "https://www.cookstr.com/recipes"

    def get_links(self, dom: html.Element) -> Sequence[str]:
        return [
            element.attrib["href"]
            for element in dom.cssselect("div.articleList2 > div.articleDiv > h4 > a")
        ]

    def get_pages(self, dom: html.Element, page: int) -> Sequence[int]:
        if page > 1:
            return []

        pages = []
        for element in dom.cssselect("div.paginationDiv > ul > li > a > span"):
            try:
                pages.append(int(element.text))
            except (ValueError, TypeError):
                pass

        if not pages:
            LOGGER.error("No more pages found after %d", page)
            return []

        return list(range(2, pages[-1] + 1))

    def get_page_url(self, page: int) -> str:
        return f"{self.start_url}/page/{page}"

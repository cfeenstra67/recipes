from typing import Sequence
from urllib.parse import urljoin

from lxml import html

from recipes.site_listers.base import StructuredSiteLister


class WikibooksLister(StructuredSiteLister):
    """ """

    start_url = "https://en.wikibooks.org/wiki/Category:Recipes"

    def get_links(self, dom: html.Element) -> Sequence[str]:
        out = []
        for element in dom.cssselect("div#mw-pages div.mw-content-ltr ul > li > a"):
            out.append(element.attrib["href"])
        return out

    def get_pages(self, dom: html.Element, page: int) -> Sequence[int]:
        links = dom.cssselect("div#mw-pages > a")
        for link in links:
            if "next page" in link.text:
                return [link.attrib["href"]]
        return []

    def get_page_url(self, page: int) -> str:
        return urljoin(self.start_url, page)

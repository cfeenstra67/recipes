from typing import Sequence

from lxml import html

from scraping.site_listers.base import StructuredSiteLister


class JustBentoLister(StructuredSiteLister):
    """
    """
    start_url = "https://justbento.com/recipes/all"
    start_page = 0

    def get_links(self, dom: html.Element) -> Sequence[str]:
        return [
            element.attrib["href"]
            for element in dom.cssselect("table.views-table tbody > tr > td.views-field-title > a")
        ]

    def get_pages(self, dom: html.Element, page: int) -> Sequence[int]:
        if page > 0:
            return []

        pager_items = dom.cssselect("ul.pager > li.pager-item > a")
        last_page = int(pager_items[-1].text) - 1

        return list(range(1, last_page))

    def get_page_url(self, page: int) -> str:
        return f"{self.start_url}?fwp_paged={page}"

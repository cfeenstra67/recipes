from typing import Sequence

from lxml import html

from recipes.site_listers.base import StructuredSiteLister


class TastyKitchenLister(StructuredSiteLister):
    """ """

    start_url = "https://tastykitchen.com/recipes/?view=title"

    def get_page_url(self, page: int) -> str:
        return f"https://tastykitchen.com/recipes/page/{page}/?view=title"

    def get_links(self, dom: html.Element) -> Sequence[str]:
        out = []
        for element in dom.cssselect("div.recent-recipe div.recent-recipe-thumb > a"):
            out.append(element.attrib["href"])
        return out

    def get_pages(self, dom: html.Element, page: int) -> Sequence[int]:
        if page > self.start_page:
            return []

        last_page = dom.cssselect("div.paged-comments > a.page-numbers:not(.next)")[-1]
        max_page = int(last_page.text.strip().replace(",", ""))
        return range(self.start_page + 1, max_page + 1)

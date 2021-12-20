import logging
import re
from typing import Iterator
from urllib.parse import urljoin, urlparse

import scrapy
from lxml import html

from recipes.site_listers.base import PageCallback, SiteLister


LOGGER = logging.getLogger(__name__)


class AmbitiousKitchenLister(SiteLister):
    """ """

    start_url = "https://www.ambitiouskitchen.com/recipe-index/"

    multi_recipe_regex = re.compile(r"^/[^/]*?(recipes|meals).+$", re.I)

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:
        def parse_list_page(response, page=1):

            html_data = html.fromstring(response.body)

            post_items = html_data.cssselect("div.post-item > a")

            if post_items:
                next_page = page + 1
                yield scrapy.Request(
                    f"{self.start_url}?sf_paged={next_page}",
                    callback=parse_list_page,
                    cb_kwargs={"page": next_page},
                )
            else:
                LOGGER.info("Exiting after page %d", page)

            for element in post_items:
                link = element.attrib["href"]
                absolute_link = urljoin(response.url, link)
                parsed_url = urlparse(link)
                if self.multi_recipe_regex.search(parsed_url.path):
                    continue
                yield scrapy.Request(absolute_link, callback=page_callback)

        yield scrapy.Request(self.start_url, callback=parse_list_page)

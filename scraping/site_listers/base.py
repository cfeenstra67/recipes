import abc
import logging
from typing import Iterator, Any, Sequence, Callable
from urllib.parse import urljoin

import scrapy
from lxml import html


LOGGER = logging.getLogger(__name__)

PageCallback = Callable[[scrapy.http.Response], Iterator[Any]]


class SiteLister(abc.ABC):
    """
    An object that will iterate through all recipes on a site
    """

    start_url: str

    @abc.abstractmethod
    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:
        """
        Start making requests, using page_callback with responses for
        actual recipes
        """
        raise NotImplementedError


class StructuredSiteLister(SiteLister):
    """ """

    @abc.abstractmethod
    def get_links(self, dom: html.Element) -> Sequence[str]:
        """ """
        raise NotImplementedError

    @abc.abstractmethod
    def get_pages(self, dom: html.Element, page: int) -> Sequence[int]:
        """ """
        raise NotImplementedError

    @abc.abstractmethod
    def get_page_url(self, page: int) -> str:
        """ """
        raise NotImplementedError

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:
        def parse_list_page(response, page: int = 1):
            html_data = html.fromstring(response.body)

            new_pages = self.get_pages(html_data, page)
            if new_pages:
                for page_num in new_pages:
                    yield scrapy.Request(
                        self.get_page_url(page_num),
                        callback=parse_list_page,
                        cb_kwargs={"page": page_num},
                        dont_filter=True,
                    )
            else:
                LOGGER.warning("No new page numbers found on page %d", page)

            for link in self.get_links(html_data):
                url = urljoin(response.url, link)
                yield scrapy.Request(url, callback=page_callback)

        yield scrapy.Request(self.start_url, callback=parse_list_page, dont_filter=True)

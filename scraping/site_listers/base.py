import abc
import logging
import re
from typing import Iterator, Any, Sequence, Callable, Optional, Dict
from urllib.parse import urljoin, urlparse

import scrapy
from lxml import html, etree


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

    start_page: int = 1

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
        def parse_list_page(response, page: int = self.start_page):
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


class SitemapLister(SiteLister):
    """ """

    extra_start_urls = ()
    recipes_path_regex: Optional[re.Pattern] = None

    namespaces: Dict[str, str] = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    def get_start_urls(self) -> Sequence[str]:
        return [self.start_url] + list(self.extra_start_urls)

    def process_start_urls(
        self, urls: Sequence[str], callback: PageCallback
    ) -> Iterator[scrapy.Request]:
        for url in urls:
            yield scrapy.Request(url, callback=callback, dont_filter=True)

    def get_sitemap_urls(self, tree: etree.Element) -> Iterator[str]:
        for location in tree.findall(
            ".//sm:sitemap/sm:loc", namespaces=self.namespaces
        ):
            yield location.text

    def get_page_urls(self, tree: etree.Element) -> Iterator[str]:
        for location in tree.findall(".//sm:url/sm:loc", namespaces=self.namespaces):
            yield location.text

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:
        def parse_sitemap(response: scrapy.http.Response):
            tree = etree.fromstring(response.body)
            for relative_url in self.get_page_urls(tree):
                url = urljoin(response.url, relative_url)
                parsed_url = urlparse(url)
                if (
                    self.recipes_path_regex is not None
                    and not self.recipes_path_regex.search(parsed_url.path)
                ):
                    continue
                yield scrapy.Request(url, callback=page_callback)

        start_urls = self.get_start_urls()
        yield from self.process_start_urls(start_urls, parse_sitemap)

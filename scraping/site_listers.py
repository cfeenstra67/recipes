import abc
import dataclasses as dc
import logging
import re
from typing import Callable, Any, Iterator, Sequence, Optional
from urllib.parse import urlencode, urlparse, urljoin

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


class ACoupleCooksLister(SiteLister):
    """
    """
    start_url = "https://www.acouplecooks.com/category/recipes/"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        def handle_list_page(response: scrapy.http.Response, page: int = 1):
            if response.status == 404:
                LOGGER.info("Page %d does not exist, exiting", page)
                return

            next_page = page + 1
            yield scrapy.Request(
                f"{self.start_url}?_paged={next_page}",
                callback=handle_list_page,
                cb_kwargs={"page": next_page},
                dont_filter=True
            )

            html_data = html.fromstring(response.body)
            for post in html_data.cssselect(
                "div.archive-post-listing > article.post-summary"
            ):
                link = post.cssselect("a")[0].attrib["href"]
                absolute_link = urljoin(response.url, link)
                yield scrapy.Request(link, callback=page_callback)

        yield scrapy.Request(self.start_url, callback=handle_list_page, dont_filter=True)


class AllRecipesLister(SiteLister):
    """
    """
    start_url = "https://www.allrecipes.com/sitemap.xml"

    recipe_map_regex = re.compile(r"^/sitemaps/recipe/\d+/sitemap\.xml$")

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        def parse_individual_sitemap(response: scrapy.http.Response):
            tree = etree.fromstring(response.body)
            for location in tree.findall(".//sm:url/sm:loc", namespaces=namespaces):
                yield scrapy.Request(urljoin(response.url, location.text), callback=page_callback)

        def parse_sitemap(response: scrapy.http.Response):
            tree = etree.fromstring(response.body)
            for location in tree.findall(".//sm:sitemap/sm:loc", namespaces=namespaces):
                parsed_url = urlparse(location.text)
                if not self.recipe_map_regex.search(parsed_url.path):
                    continue
                yield scrapy.Request(
                    location.text,
                    callback=parse_individual_sitemap,
                    dont_filter=True
                )

        yield scrapy.Request(self.start_url, callback=parse_sitemap, dont_filter=True)


class AmbitiousKitchenLister(SiteLister):
    """
    """
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
                    cb_kwargs={"page": next_page}
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


class ArchanasKitchenLister(SiteLister):
    """
    """
    start_url = "https://www.archanaskitchen.com/recipes"

    page_url_regex = re.compile(r"^/recipes/page-(\d+)$")

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        def parse_single_list_page(response):
            html_data = html.fromstring(response.body)

            blog_links = html_data.cssselect("div.blogRecipe > div > a")
            for link in blog_links:
                absolute_link = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(absolute_link, callback=page_callback)

        def parse_first_list_page(response):

            html_data = html.fromstring(response.body)

            end_link = html_data.find(".//div[@class=\"pagination\"]//a[@title=\"End\"]")
            if end_link is None:
                LOGGER.error("Unable to find last page.")
                yield from parse_single_list_page(response)
                return

            parsed_link = urlparse(end_link.attrib["href"])
            match = self.page_url_regex.search(parsed_link.path)
            if not match:
                LOGGER.error("No match found for page number in path: %s", parsed_link.path)
                yield from parse_single_list_page(response)
                return

            last_page = int(match.group(1))

            LOGGER.info("Last page: %d", last_page)

            for page_num in range(2, last_page + 1):
                yield scrapy.Request(
                    f"{self.start_url}/page-{page_num}",
                    callback=parse_single_list_page,
                    dont_filter=True
                )

            yield from parse_single_list_page(response)

        yield scrapy.Request(self.start_url, callback=parse_first_list_page, dont_filter=True)


class AverieCooksLister(SiteLister):
    """
    """
    start_url = "https://www.averiecooks.com/category/recipes/"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        def parse_single_list_page(response):
            html_data = html.fromstring(response.body)
            for link in html_data.cssselect("div.archives > div.archive-post > a"):
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(url, callback=page_callback)

        def parse_first_list_page(response):
            html_data = html.fromstring(response.body)
            page_nums = html_data.cssselect("div.nav-links > a.page-numbers")
            pages = []
            for element in page_nums:
                try:
                    pages.append(int(element.text))
                except ValueError:
                    pass

            if not pages:
                LOGGER.error("No page numbers found.")
            else:
                LOGGER.info("Last page: %d", pages[-1])
                for page_num in range(2, pages[-1] + 1):
                    yield scrapy.Request(
                        f"{self.start_url}page/{page_num}",
                        callback=parse_single_list_page,
                        dont_filter=True
                    )

            yield from parse_single_list_page(response)

        yield scrapy.Request(self.start_url, callback=parse_first_list_page, dont_filter=True)


class BakingSenseLister(SiteLister):
    """
    """
    start_url = "https://www.baking-sense.com/category/recipes/"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        def parse_single_list_page(response):
            html_data = html.fromstring(response.body)
            for link in html_data.cssselect("main.content-container > article.article.excerpt a"):
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(url, callback=page_callback, dont_filter=True)

        def parse_first_list_page(response):
            html_data = html.fromstring(response.body)
            page_nums = html_data.cssselect("div.nav-links > a.page-numbers")
            pages = []
            for element in page_nums:
                try:
                    pages.append(int(element.text))
                except ValueError:
                    pass

            if not pages:
                LOGGER.error("No page numbers found.")
            else:
                LOGGER.info("Last page: %d", pages[-1])
                for page_num in range(2, pages[-1] + 1):
                    yield scrapy.Request(
                        f"{self.start_url}page/{page_num}",
                        callback=parse_single_list_page,
                        dont_filter=True
                    )

            yield from parse_single_list_page(response)

        yield scrapy.Request(self.start_url, callback=parse_first_list_page)


class BakingMischiefLister(SiteLister):
    """
    """
    start_url = "https://bakingmischief.com/category/recipes/"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        def parse_single_list_page(response):
            html_data = html.fromstring(response.body)
            for link in html_data.cssselect("main.content > article.post a"):
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(url, callback=page_callback)

        def parse_first_list_page(response):
            html_data = html.fromstring(response.body)
            page_nums = html_data.cssselect("div.pagination > ul > li > a")
            pages = []
            for element in page_nums:
                try:
                    pages.append(int(element.text))
                except ValueError:
                    pass

            if not pages:
                LOGGER.error("No page numbers found.")
            else:
                LOGGER.info("Last page: %d", pages[-1])
                for page_num in range(2, pages[-1] + 1):
                    yield scrapy.Request(
                        f"{self.start_url}page/{page_num}",
                        callback=parse_single_list_page,
                        dont_filter=True
                    )

            yield from parse_single_list_page(response)

        yield scrapy.Request(self.start_url, callback=parse_first_list_page, dont_filter=True)


class BBCLister(SiteLister):
    """
    """
    start_url = "https://www.bbc.co.uk/food/recipes/a-z"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        def parse_single_list_page(response):
            html_data = html.fromstring(response.body)
            for link in html_data.cssselect("div.promo-collection > div > a.promo"):
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(url, callback=page_callback)

        def parse_first_list_page(response, letter):
            html_data = html.fromstring(response.body)
            page_nums = html_data.cssselect("div.pagination > ul > li > a")
            pages = []
            for element in page_nums:
                try:
                    pages.append(int(element.text))
                except (ValueError, TypeError):
                    pass

            if not pages:
                LOGGER.error("No page numbers found.")
            else:
                LOGGER.info("Last page: %d", pages[-1])
                for page_num in range(2, pages[-1] + 1):
                    yield scrapy.Request(
                        f"{self.start_url}/{letter}/{page_num}",
                        callback=parse_single_list_page,
                        dont_filter=True
                    )

            yield from parse_single_list_page(response)

        letters = list(map(lambda x: chr(ord('a') + x), range(26)))
        letters.append("0-9")

        for letter in letters:
            yield scrapy.Request(
                f"{self.start_url}/{letter}",
                callback=parse_first_list_page,
                cb_kwargs={"letter": letter},
                dont_filter=True
            )


class BBCGoodFoodLister(SiteLister):
    """
    """
    start_url = "https://www.bbcgoodfood.com/sitemap.xml"

    recipe_url_regex = re.compile(r"^/recipes/.+$")

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        def parse_individual_sitemap(response: scrapy.http.Response):
            tree = etree.fromstring(response.body)
            for location in tree.findall(".//sm:url/sm:loc", namespaces=namespaces):
                url = urljoin(response.url, location.text)
                parsed_url = urlparse(url)
                if not self.recipe_url_regex.search(parsed_url.path):
                    continue
                yield scrapy.Request(url, callback=page_callback)

        def parse_sitemap(response: scrapy.http.Response):
            tree = etree.fromstring(response.body)
            for location in tree.findall(".//sm:sitemap/sm:loc", namespaces=namespaces):
                yield scrapy.Request(
                    urljoin(response.url, location.text),
                    callback=parse_individual_sitemap,
                    dont_filter=True
                )

        yield scrapy.Request(self.start_url, callback=parse_sitemap, dont_filter=True)


class BettyCrockerLister(SiteLister):
    """
    """
    start_url = "https://www.bettycrocker.com/recipe.xml"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        def parse_sitemap(response: scrapy.http.Response):
            tree = etree.fromstring(response.body)
            for location in tree.findall(".//sm:url/sm:loc", namespaces=namespaces):
                yield scrapy.Request(
                    urljoin(response.url, location.text),
                    callback=page_callback,
                    dont_filter=True
                )

        yield scrapy.Request(self.start_url, callback=parse_sitemap, dont_filter=True)


class BonAppetitLister(SiteLister):
    """
    """
    start_url = "https://www.bonappetit.com/sitemap.xml"

    recipe_url_regex = re.compile(r"^/recipe/.+$")

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        def parse_individual_sitemap(response: scrapy.http.Response):
            tree = etree.fromstring(response.body)
            for location in tree.findall(".//sm:url/sm:loc", namespaces=namespaces):
                url = urljoin(response.url, location.text)
                parsed_url = urlparse(url)
                if not self.recipe_url_regex.search(parsed_url.path):
                    continue
                yield scrapy.Request(url, callback=page_callback)

        def parse_sitemap(response: scrapy.http.Response):
            tree = etree.fromstring(response.body)
            for location in tree.findall(".//sm:sitemap/sm:loc", namespaces=namespaces):
                yield scrapy.Request(
                    urljoin(response.url, location.text),
                    callback=parse_individual_sitemap,
                    dont_filter=True
                )

        yield scrapy.Request(self.start_url, callback=parse_sitemap, dont_filter=True)


class BowlOfDeliciousLister(SiteLister):
    """
    """
    start_url = "https://www.bowlofdelicious.com/category/recipes/"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        def parse_single_list_page(response):
            html_data = html.fromstring(response.body)
            for link in html_data.cssselect("main.content > article.post a"):
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(url, callback=page_callback)

        def parse_first_list_page(response):
            html_data = html.fromstring(response.body)
            page_nums = html_data.cssselect("div.pagination > ul > li > a")
            pages = []
            for element in page_nums:
                try:
                    pages.append(int(element[0].tail))
                except (ValueError, TypeError, IndexError):
                    pass

            if not pages:
                LOGGER.error("No page numbers found.")
            else:
                LOGGER.info("Last page: %d", pages[-1])
                for page_num in range(2, pages[-1] + 1):
                    yield scrapy.Request(
                        f"{self.start_url}page/{page_num}",
                        callback=parse_single_list_page,
                        dont_filter=True
                    )

            yield from parse_single_list_page(response)

        yield scrapy.Request(self.start_url, callback=parse_first_list_page, dont_filter=True)


class BudgetBytesLister(SiteLister):
    """
    """
    start_url = "https://www.budgetbytes.com/category/recipes/"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        def parse_single_list_page(response):
            html_data = html.fromstring(response.body)
            for link in html_data.cssselect("div#content > article.post a"):
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(url, callback=page_callback)

        def parse_first_list_page(response):
            html_data = html.fromstring(response.body)
            page_nums = html_data.cssselect("div.nav-links > a.page-numbers")
            pages = []
            for element in page_nums:
                try:
                    pages.append(int(element.text))
                except ValueError:
                    pass

            if not pages:
                LOGGER.error("No page numbers found.")
            else:
                LOGGER.info("Last page: %d", pages[-1])
                for page_num in range(2, pages[-1] + 1):
                    yield scrapy.Request(
                        f"{self.start_url}page/{page_num}",
                        callback=parse_single_list_page,
                        dont_filter=True
                    )

            yield from parse_single_list_page(response)

        yield scrapy.Request(self.start_url, callback=parse_first_list_page, dont_filter=True)


class CastIronKetoLister(SiteLister):
    """
    """
    start_url = "https://www.castironketo.net/blog/category/recipe/"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        def parse_single_list_page(response):
            html_data = html.fromstring(response.body)
            for link in html_data.cssselect("main.content > article.post a"):
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(url, callback=page_callback)

        def parse_first_list_page(response):
            html_data = html.fromstring(response.body)
            page_nums = html_data.cssselect("div.pagination > ul > li > a")
            pages = []
            for element in page_nums:
                try:
                    pages.append(int(element[0].tail.strip()))
                except (ValueError, TypeError, IndexError, AttributeError):
                    pass

            if not pages:
                LOGGER.error("No page numbers found.")
            else:
                LOGGER.info("Last page: %d", pages[-1])
                for page_num in range(2, pages[-1] + 1):
                    yield scrapy.Request(
                        f"{self.start_url}page/{page_num}",
                        callback=parse_single_list_page,
                        dont_filter=True
                    )

            yield from parse_single_list_page(response)

        yield scrapy.Request(self.start_url, callback=parse_first_list_page, dont_filter=True)


class ClosetCookingLister(SiteLister):
    """
    """
    start_url = "https://www.closetcooking.com/category/recipe/"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        def parse_single_list_page(response):
            html_data = html.fromstring(response.body)
            for link in html_data.cssselect("main.content > article.post a"):
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(url, callback=page_callback)

        def parse_first_list_page(response):
            html_data = html.fromstring(response.body)
            page_nums = html_data.cssselect("div.pagination > ul > li > a")
            pages = []
            for element in page_nums:
                try:
                    pages.append(int(element[0].tail.strip()))
                except (ValueError, TypeError, IndexError, AttributeError):
                    pass

            if not pages:
                LOGGER.error("No page numbers found.")
            else:
                LOGGER.info("Last page: %d", pages[-1])
                for page_num in range(2, pages[-1] + 1):
                    yield scrapy.Request(
                        f"{self.start_url}page/{page_num}",
                        callback=parse_single_list_page,
                        dont_filter=True
                    )

            yield from parse_single_list_page(response)

        yield scrapy.Request(self.start_url, callback=parse_first_list_page, dont_filter=True)


class CookEatShareLister(SiteLister):
    """
    """
    start_url = "https://cookeatshare.com/recipes"

    def start_requests(self, page_callback: PageCallback) -> Iterator[scrapy.Request]:

        def parse_single_list_page(response):
            html_data = html.fromstring(response.body)
            for link in html_data.cssselect("table.recipes tr a.recipe-link"):
                url = urljoin(response.url, link.attrib["href"])
                yield scrapy.Request(url, callback=page_callback)

        def parse_first_list_page(response):
            html_data = html.fromstring(response.body)
            page_nums = html_data.cssselect("div.pagination > a")
            pages = []
            for element in page_nums:
                try:
                    pages.append(int(element.text))
                except (ValueError, TypeError):
                    pass

            if not pages:
                LOGGER.error("No page numbers found.")
            else:
                LOGGER.info("Last page: %d", pages[-1])
                for page_num in range(2, pages[-1] + 1):
                    yield scrapy.Request(
                        f"{self.start_url}/page/{page_num}",
                        callback=parse_single_list_page,
                        dont_filter=True
                    )

            yield from parse_single_list_page(response)

        yield scrapy.Request(self.start_url, callback=parse_first_list_page, dont_filter=True)


class StructuredSiteLister(SiteLister):
    """
    """
    @abc.abstractmethod
    def get_links(self, dom: html.Element) -> Sequence[str]:
        """
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_pages(self, dom: html.Element, page: int) -> Sequence[int]:
        """
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_page_url(self, page: int) -> str:
        """
        """
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
                        dont_filter=True
                    )
            else:
                LOGGER.warning("No new page numbers found on page %d", page)

            for link in self.get_links(html_data):
                url = urljoin(response.url, link)
                yield scrapy.Request(url, callback=page_callback)

        yield scrapy.Request(self.start_url, callback=parse_list_page, dont_filter=True)


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


class CookStrLister(StructuredSiteLister):
    """
    """
    start_url = "https://www.cookstr.com/recipes"

    def get_links(self, dom: html.Element) -> Sequence[str]:
        return [
            element.attrib["href"] for element in dom.cssselect(
                "div.articleList2 > div.articleDiv > h4 > a"
            )
        ]

    def get_pages(self, dom: html.Element, page: int) -> Sequence[int]:
        if page > 1:
            return []

        pages = []
        for el in dom.cssselect("div.paginationDiv > ul > li > a > span"):
            try:
                pages.append(int(el.text))
            except (ValueError, TypeError):
                pass

        if not pages:
            LOGGER.error("No more pages found after %d", page)
            return []

        return list(range(2, pages[-1] + 1))

    def get_page_url(self, page: int) -> str:
        return f"{self.start_url}/page/{page}"


class EatingBirdFoodLister(StructuredSiteLister):
    """
    """
    start_url = "https://www.eatingbirdfood.com/recipe-index/"

    def get_links(self, dom: html.Element) -> Sequence[str]:
        return [
            element.attrib["href"] for element in dom.cssselect(
                "div.search-filter-results > div.single-posty > a"
            )
        ]

    def get_pages(self, dom: html.Element, page: int) -> Sequence[int]:
        if not self.get_links(dom):
            return []
        return [page + 1]

    def get_page_url(self, page: int) -> str:
        return f"{self.start_url}?sf_paged={page}"

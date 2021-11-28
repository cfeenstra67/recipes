import re

from scraping.site_listers.base import SitemapLister


class SunBasketLister(SitemapLister):
    """
    """
    start_url = "https://sunbasket.com/sitemap.xml"
    recipes_path_regex = re.compile(r"^/recipe/.+$")

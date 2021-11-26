import re

from scraping.site_listers.base import SitemapLister


class InnitLister(SitemapLister):
    """ """

    start_url = "https://www.innit.com/meal/sitemap.xml"
    recipes_path_regex = re.compile(r"^/meal/.+$")

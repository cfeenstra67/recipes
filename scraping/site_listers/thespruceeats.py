import re
from scraping.site_listers.base import SitemapLister


class TheSpruceEatsLister(SitemapLister):
    """
    """
    start_url = "https://www.thespruceeats.com/sitemap_1.xml"
    recipes_path_regex = re.compile(r"^/.*recipe.*$")

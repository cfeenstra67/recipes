import re

from scraping.site_listers.base import SitemapLister


class JimCooksGoodFoodLister(SitemapLister):
    """
    """
    start_url = "https://jimcooksfoodgood.com/post-sitemap.xml"
    recipes_path_regex = re.compile(r"^/.+$")

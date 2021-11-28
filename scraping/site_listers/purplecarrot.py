import re

from scraping.site_listers.base import SitemapLister


class PurpleCarrotLister(SitemapLister):
    """
    """
    start_url = "https://www.purplecarrot.com/sitemap.xml"
    recipes_path_regex = re.compile(r"^/plant-based-recipes/.+$")

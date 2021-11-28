import re

from scraping.site_listers.base import TwoLevelSitemapLister


class TasteOfHomeLister(TwoLevelSitemapLister):
    """
    """
    start_url = "https://www.tasteofhome.com/sitemap_index.xml"
    sitemap_path_regex = re.compile(r"^/recipe-sitemap\d+\.xml$")
    recipes_path_regex = re.compile(r"^/recipes/.+$")

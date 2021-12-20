import re

from scraping.site_listers.base import TwoLevelSitemapLister


class TheHappyFoodieLister(TwoLevelSitemapLister):
    """ """

    start_url = "https://thehappyfoodie.co.uk/sitemap_index.xml"
    sitemap_path_regex = re.compile(r"^/recipes-sitemap\d+\.xml$")
    recipes_path_regex = re.compile(r"^/recipes/.+$")

import re

from scraping.site_listers.base import SitemapLister


class JamieOliverLister(SitemapLister):
    """
    """
    start_url = "https://www.jamieoliver.com/recipes.xml"
    recipes_path_regex = re.compile(r"^/recipes/.+$")

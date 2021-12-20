import re

from scraping.site_listers.base import TwoLevelSitemapLister


class TheKitchnLister(TwoLevelSitemapLister):
    """ """

    start_url = "https://www.thekitchn.com/sitemap.xml"
    sitemap_path_regex = re.compile(r"^/sitemap-\d+-\d+\.xml$")
    recipes_path_regex = re.compile(r"^/.*recipe.*$")

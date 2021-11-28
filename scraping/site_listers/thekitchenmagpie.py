import re

from scraping.site_listers.base import TwoLevelSitemapLister


class TheKitchenMagpieLister(TwoLevelSitemapLister):
    """
    """
    start_url = "https://www.thekitchenmagpie.com/sitemap_index.xml"
    sitemap_path_regex = re.compile(r"^/post-sitemap\d+\.xml$")

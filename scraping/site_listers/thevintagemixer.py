import re

from scraping.site_listers.base import TwoLevelSitemapLister


class TheVintageMixerLister(TwoLevelSitemapLister):
    """ """

    start_url = "https://www.thevintagemixer.com/sitemap.xml"
    sitemap_path_regex = re.compile(r"^/sitemap-pt-post-\d+-\d+\.xml$")

import re

from scraping.site_listers.base import TwoLevelSitemapLister


class PracticalSelfRelianceLister(TwoLevelSitemapLister):
    """ """

    start_url = "https://practicalselfreliance.com/sitemap.xml"
    sitemap_path_regex = re.compile(r"^/sitemap-pt-post-\d+-\d+\.xml$")

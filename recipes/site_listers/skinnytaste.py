import re

from recipes.site_listers.base import TwoLevelSitemapLister


class SkinnyTasteLister(TwoLevelSitemapLister):
    """ """

    start_url = "https://www.skinnytaste.com/sitemap_index.xml"
    sitemap_path_regex = re.compile(r"^/post-sitemap\d+\.xml$")

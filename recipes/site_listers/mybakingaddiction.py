import re

from recipes.site_listers.base import TwoLevelSitemapLister


class MyBakingAddictionLister(TwoLevelSitemapLister):
    """ """

    start_url = "https://www.mybakingaddiction.com/sitemap.xml"
    sitemap_path_regex = re.compile(r"^/sitemap-pt-post-\d+-\d+\.xml$")

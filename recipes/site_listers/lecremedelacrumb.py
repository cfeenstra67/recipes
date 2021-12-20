import re

from recipes.site_listers.base import SitemapLister


class LeCremeDeLaCrumbLister(SitemapLister):
    """ """

    start_url = "https://www.lecremedelacrumb.com/post-sitemap1.xml"
    extra_start_urls = ["https://www.lecremedelacrumb.com/post-sitemap2.xml"]
    recipes_path_regex = re.compile(r"^/.+$")

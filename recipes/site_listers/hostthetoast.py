import re

from recipes.site_listers.base import SitemapLister


class HostTheToastLister(SitemapLister):
    """ """

    start_url = "https://hostthetoast.com/post-sitemap.xml"
    recipes_path_regex = re.compile(r"^/.+$")

import re

from recipes.site_listers.base import TwoLevelSitemapLister


class SaveurLister(TwoLevelSitemapLister):
    """ """

    start_url = "https://www.saveur.com/sitemap_index.xml"
    sitemap_path_regex = re.compile(r"^/post-sitemap\d+\.xml$")
    recipes_path_regex = re.compile(r"^/article/Recipes/.+$")

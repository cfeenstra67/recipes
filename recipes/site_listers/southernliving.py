import re

from recipes.site_listers.base import SitemapLister


class SouthernLivingLister(SitemapLister):
    """ """

    start_url = "https://www.southernliving.com/sitemaps/recipe/1/sitemap.xml"
    recipes_path_regex = re.compile(r"^/recipes/.+$")

import re

from recipes.site_listers.base import SitemapLister


class SimplyRecipesLister(SitemapLister):
    """ """

    start_url = "https://www.simplyrecipes.com/sitemap_1.xml"
    recipes_path_regex = re.compile(r"^/recipes/.+$")

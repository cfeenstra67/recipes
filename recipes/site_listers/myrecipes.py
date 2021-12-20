import re

from recipes.site_listers.base import SitemapLister


class MyRecipesLister(SitemapLister):
    """ """

    start_url = "https://www.myrecipes.com/sitemaps/recipe/1/sitemap.xml"
    extra_start_urls = [
        "https://www.myrecipes.com/sitemaps/recipe/2/sitemap.xml",
        "https://www.myrecipes.com/sitemaps/recipe/3/sitemap.xml",
    ]
    recipes_path_regex = re.compile(r"^/recipe/.+$")

from recipes.site_listers.base import SitemapLister


class RecipeTinEatsLister(SitemapLister):
    """ """

    start_url = "https://www.recipetineats.com/post-sitemap1.xml"
    extra_start_urls = ["https://www.recipetineats.com/post-sitemap2.xml"]

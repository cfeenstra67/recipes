from scraping.site_listers.base import SitemapLister


class VegRecipesOfIndiaLister(SitemapLister):
    """
    """
    start_url = "https://www.vegrecipesofindia.com/post-sitemap1.xml"
    extra_start_urls = [
        "https://www.vegrecipesofindia.com/post-sitemap2.xml"
    ]

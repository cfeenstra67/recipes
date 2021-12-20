from recipes.site_listers.base import SitemapLister


class JustATasteLister(SitemapLister):
    """ """

    start_url = "https://www.justataste.com/post-sitemap1.xml"
    extra_start_urls = ["https://www.justataste.com/post-sitemap2.xml"]

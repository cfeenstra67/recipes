from recipes.site_listers.base import SitemapLister


class _101CookbooksLister(SitemapLister):
    """ """

    start_url = "https://101cookbooks.com/post-sitemap1.xml"
    extra_start_urls = ["https://101cookbooks.com/post-sitemap2.xml"]

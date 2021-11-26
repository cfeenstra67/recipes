from scraping.site_listers.base import SitemapLister


class MarthaStewartLister(SitemapLister):
    """ """

    start_url = "https://www.marthastewart.com/sitemaps/recipe/1/sitemap.xml"
    extra_start_urls = ["https://www.marthastewart.com/sitemaps/recipe/2/sitemap.xml"]

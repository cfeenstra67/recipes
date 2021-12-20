from scraping.site_listers.base import SitemapLister


class VanillaAndBeanLister(SitemapLister):
    """ """

    start_url = "https://vanillaandbean.com/post-sitemap1.xml"
    extra_start_urls = ["https://vanillaandbean.com/post-sitemap2.xml"]

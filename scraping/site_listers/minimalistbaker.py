from scraping.site_listers.base import SitemapLister


class MinimalistBakerLister(SitemapLister):
    """ """

    start_url = "https://minimalistbaker.com/post-sitemap1.xml"
    extra_start_urls = ["https://minimalistbaker.com/post-sitemap2.xml"]

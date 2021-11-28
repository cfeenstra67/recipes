from scraping.site_listers.base import SitemapLister


class SimplyQuinoaLister(SitemapLister):
    """
    """
    start_url = "https://www.simplyquinoa.com/post-sitemap1.xml"
    extra_start_urls = [
        "https://www.simplyquinoa.com/post-sitemap2.xml"
    ]

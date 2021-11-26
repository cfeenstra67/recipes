from scraping.site_listers.base import SitemapLister


class MelsKitchenCafeLister(SitemapLister):
    """
    """
    start_url = "https://www.melskitchencafe.com/post-sitemap1.xml"
    extra_start_urls = [
        "https://www.melskitchencafe.com/post-sitemap2.xml"
    ]

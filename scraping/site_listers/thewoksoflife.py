from scraping.site_listers.base import SitemapLister


class TheWoksOfLifeLister(SitemapLister):
    """
    """
    start_url = "https://thewoksoflife.com/post-sitemap1.xml"
    extra_start_urls = [
        "https://thewoksoflife.com/post-sitemap2.xml"
    ]

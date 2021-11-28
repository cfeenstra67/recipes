from scraping.site_listers.base import SitemapLister


class SweetCsDesignsLister(SitemapLister):
    """
    """
    start_url = "https://sweetcsdesigns.com/post-sitemap1.xml"
    extra_start_urls = [
        "https://sweetcsdesigns.com/post-sitemap2.xml"
    ]

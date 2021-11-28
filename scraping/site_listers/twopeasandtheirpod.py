from scraping.site_listers.base import SitemapLister


class TwoPeasAndTheirPodLister(SitemapLister):
    """
    """
    start_url = "https://www.twopeasandtheirpod.com/post-sitemap1.xml"
    extra_start_urls = [
        "https://www.twopeasandtheirpod.com/post-sitemap2.xml",
        "https://www.twopeasandtheirpod.com/post-sitemap3.xml"
    ]

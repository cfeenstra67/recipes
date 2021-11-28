from scraping.site_listers.base import SitemapLister


class WhatsGabyCookingLister(SitemapLister):
    """
    """
    start_url = "https://whatsgabycooking.com/post-sitemap1.xml"
    extra_start_urls = [
        "https://whatsgabycooking.com/post-sitemap2.xml"
    ]

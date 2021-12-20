from scraping.site_listers.base import SitemapLister


class SteamyKitchenLister(SitemapLister):
    """ """

    start_url = "https://steamykitchen.com/wp-sitemap-posts-post-1.xml"
    extra_start_urls = ["https://steamykitchen.com/wp-sitemap-posts-post-2.xml"]

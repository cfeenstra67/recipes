from scraping.site_listers.base import SitemapLister


class SpendWithPenniesLister(SitemapLister):
    """ """

    start_url = "https://spendwithpennies.com/post-sitemap1.xml"
    extra_start_urls = [
        "https://spendwithpennies.com/post-sitemap2.xml",
        "https://spendwithpennies.com/post-sitemap3.xml",
    ]

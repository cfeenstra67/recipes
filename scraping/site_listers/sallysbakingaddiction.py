from scraping.site_listers.base import SitemapLister


class SallysBakingAddictionLister(SitemapLister):
    """ """

    start_url = "http://sallysbakingaddiction.com/post-sitemap1.xml"
    extra_start_urls = ["http://sallysbakingaddiction.com/post-sitemap2.xml"]

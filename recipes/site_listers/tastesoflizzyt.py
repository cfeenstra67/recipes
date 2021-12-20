from recipes.site_listers.base import SitemapLister


class TastesOfLizzyTLister(SitemapLister):
    """ """

    start_url = "https://www.tastesoflizzyt.com/post-sitemap1.xml"
    extra_start_urls = ["https://www.tastesoflizzyt.com/post-sitemap2.xml"]

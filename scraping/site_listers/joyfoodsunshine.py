import re

from scraping.site_listers.base import SitemapLister


class JoyFoodSunshineLister(SitemapLister):
    """ """

    start_url = "https://joyfoodsunshine.com/post-sitemap.xml"
    recipes_path_regex = re.compile(r"^/.+$")

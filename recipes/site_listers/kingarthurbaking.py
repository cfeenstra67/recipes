import re

from recipes.site_listers.base import SitemapLister


class KingArthurBakingLister(SitemapLister):
    """ """

    start_url = "https://www.kingarthurbaking.com/sitemap.xml?page=1"
    extra_start_urls = [
        "https://www.kingarthurbaking.com/sitemap.xml?page=2",
        "https://www.kingarthurbaking.com/sitemap.xml?page=3",
        "https://www.kingarthurbaking.com/sitemap.xml?page=4",
    ]
    recipes_path_regex = re.compile(r"^/recipes/.+$")

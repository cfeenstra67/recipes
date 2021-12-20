# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RecipeItem(scrapy.Item):
    """ """

    title = scrapy.Field()
    total_time = scrapy.Field()
    yields = scrapy.Field()
    ingredients = scrapy.Field()
    instructions = scrapy.Field()
    image = scrapy.Field()
    host = scrapy.Field()
    nutrients = scrapy.Field()
    html = scrapy.Field()
    url = scrapy.Field()
    accessed_at = scrapy.Field()


class ScrapingError(scrapy.Item):
    """ """

    url = scrapy.Field()
    is_http = scrapy.Field()
    http_status = scrapy.Field()
    http_body = scrapy.Field()
    error_type = scrapy.Field()
    error_msg = scrapy.Field()
    error_traceback = scrapy.Field()

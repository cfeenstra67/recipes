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
    links = scrapy.Field()
    nutrients = scrapy.Field()
    html = scrapy.Field()
    url = scrapy.Field()
    accessed_at = scrapy.Field()

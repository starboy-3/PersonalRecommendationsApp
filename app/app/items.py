# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field


class ProductItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = Field()
    price = Field()
    description = Field()
    image_urls = Field() # ML

    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()

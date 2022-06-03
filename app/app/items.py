import scrapy
from scrapy.loader import ItemLoader


class PageItem(scrapy.Item):
    """ class represents all web-pages
        in catalog dir of parsing site
    """
    url = scrapy.Field()
    path = scrapy.Field()


class PageItemLoader(ItemLoader):
    # default_output_processor = TakeFirst()
    pass


def filter_price(value: str) -> str:
    result = value.strip().replace('₽', '').replace('\xa0', '')
    if result.isdigit():
        return result


class ProductItem(scrapy.Item):
    product_id = scrapy.Field()
    product_name = scrapy.Field()
    seller = scrapy.Field()
    seller_id = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    # features = scrapy.Field()   # store as JSON object? or should we create new tables?


class OzonProductItem(scrapy.Item):
    title = scrapy.Field()
    brand = scrapy.Field()
    category = scrapy.Field()
    link = scrapy.Field()
    price = scrapy.Field()
    sellerID = scrapy.Field()
    sellerName = scrapy.Field()
    image = scrapy.Field()
    desc = scrapy.Field()


class ProductItemLoader(ItemLoader):
    # default_output_processor = TakeFirst()
    # product_name_in = MapCompose(str.strip)
    # seller_in = MapCompose(str.strip)
    # price_in = MapCompose(filter_price)
    # description_in = MapCompose(str.strip)
    pass

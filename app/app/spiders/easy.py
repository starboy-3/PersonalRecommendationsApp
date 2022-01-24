import datetime
import socket

import scrapy
from itemloaders import ItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from app.items import ProductItem


class EasySpider(CrawlSpider):
    name = 'easy'
    allowed_domains = ['asos.com']
    start_urls = ["https://www.asos.com/ru/adidas-originals/belye-kozhanye-krossovki-adidas-originals-delpala/prd/24358304?clr=belyj&colourWayId=60575118&cid=28031"]  # TODO: Maybe https

    # rules = (
    #     Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    # )

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//div[@class="_2xLfY"]')),
        Rule(LinkExtractor(restrict_xpaths='//a[@class="_37mjk"]'),
             callback='parse_item')
    )

    def parse_item(self, response):
        l = ItemLoader(item=ProductItem(), selector=response)

        l.add_xpath('title', '/html/body/div[1]/div/main/div[2]/section[1]/div/div[2]/div[2]/div[1]/h1/text()')
        # l.add_xpath('price', '//span[@data-id="current-price"]/text()')
        l.add_css('price', 'span.current-price.product-price-discounted::text')

        l.add_xpath('description', '//div[@class="product-description"]')
        l.add_xpath('image_urls', '//img[@class="gallery-image"]/@src')

        l.add_value('url', response.url)
        l.add_value('project', self.settings.get('BOT_NAME'))
        l.add_value('spider', self.name)
        l.add_value('server', socket.gethostname())
        l.add_value('date', datetime.datetime.now())

        return l.load_item()

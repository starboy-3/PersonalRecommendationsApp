import datetime
import socket
from urllib.parse import urljoin

import scrapy
from itemloaders import ItemLoader
from scrapy import Request

from app.items import ProductItem


class ManualSpider(scrapy.Spider):
    name = 'manual'
    allowed_domains = ['asos.com']
    start_urls = [
        "https://www.asos.com/ru/adidas-originals/belye-kozhanye-krossovki-adidas-originals-delpala/prd/24358304?clr=belyj&colourWayId=60575118&cid=28031"]

    def parse_item(self, response):
        l = ItemLoader(item=ProductItem(), selector=response)

        l.add_xpath('title', '/html/body/div[1]/div/main/div[2]/section[1]/div/div[2]/div[2]/div[1]/h1/text()')
        l.add_xpath('price',
                    '/html/body/div[1]/div/main/div[2]/section[1]/div/div[2]/div[2]/div[1]/div[1]/div[1]/span[1]/text()')
        l.add_xpath('description', '//div[@class="product-description"]')
        l.add_xpath('image_urls', '//img[@class="gallery-image"]/@src')

        l.add_value('url', response.url)
        l.add_value('project', self.settings.get('BOT_NAME'))
        l.add_value('spider', self.name)
        l.add_value('server', socket.gethostname())
        l.add_value('date', datetime.datetime.now())

        return l.load_item()

    def parse(self, response):

        # Get the next index URLs and yield Requests
        next_selector = response.xpath('//*[contains(@class,'
                                       '"next")]//@href') # Find next url
        for url in next_selector.extract():
            yield Request(url=urljoin(response.url, url))
            # Get item URLs and yield Requests
            item_selector = response.xpath('//*[@itemprop="url"]/@href')
            for url in item_selector.extract():
                yield Request(url=urljoin(response.url, url),
                              callback=self.parse_item)

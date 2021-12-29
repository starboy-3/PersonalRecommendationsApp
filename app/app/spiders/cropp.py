import scrapy, datetime, socket
from itemloaders import ItemLoader
from app.items import ProductItem


class CroppSpider(scrapy.Spider):
    name = 'cropp'
    allowed_domains = ["www.cropp.com"]
    start_urls = ['https://www.cropp.com/ru/ru/7088l-01x/bluza-m-cropp']


    def parse(self, response):
        l = ItemLoader(item=ProductItem(), selector=response)

        l.add_xpath('title', '//h1[@class="product-name"]/text()')
        l.add_xpath('price', '//div[@class="promo-price"]/text()')
        l.add_xpath('description', '/html/body/div[1]/section/div[2]/div/div/section/div[2]/div/div[1]/div/div/div/div/ul')
        l.add_xpath('image_urls', '/html/body/div[1]/section/div[2]/div/div/section/section/section/aside[2]/div/div[1]/img/@src')

        l.add_value('url', response.url)
        l.add_value('project', self.settings.get('BOT_NAME'))
        l.add_value('spider', self.name)
        l.add_value('server', socket.gethostname())
        l.add_value('date', datetime.datetime.now())

        return l.load_item()

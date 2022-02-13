import scrapy
import socket, datetime

# from app.app.items import AppItem
from app.items import ProductItem
from itemloaders import ItemLoader


class AsosSpider(scrapy.Spider):
    name = 'asos'
    allowed_domains = ['asos.com']
    start_urls = ["https://www.asos.com/ru/adidas-originals/belye-kozhanye-krossovki-adidas-originals-delpala/prd/24358304?clr=belyj&colourWayId=60575118&cid=28031"]  # TODO: Maybe https

    def parse(self, response):
        l = ItemLoader(item=ProductItem(), selector=response)

        l.add_xpath('title', '/html/body/div[1]/div/main/div[2]/section[1]/div/div[2]/div[2]/div[1]/h1/text()')git
        # l.add_xpath('price', '//span[@data-id="current-price"]/text()')
        l.add_xpath('price', '/html/body/div[1]/div/main/div[2]/section[1]/div/div[2]/div[2]/div[1]/div[1]/div/span[2]/span[4]/span[1]')
        # l.add_css('price', 'span.current-price.product-price-discounted::text')

        l.add_xpath('description', '//div[@class="product-description"]')
        l.add_xpath('image_urls', '//img[@class="gallery-image"]/@src')

        l.add_value('url', response.url)
        l.add_value('project', self.settings.get('BOT_NAME'))
        l.add_value('spider', self.name)
        l.add_value('server', socket.gethostname())
        l.add_value('date', datetime.datetime.now())

        return l.load_item()


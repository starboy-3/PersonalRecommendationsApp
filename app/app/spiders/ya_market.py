import scrapy

# from app.app.items import AppItem
from app.items import AppItem


class YaMarketSpider(scrapy.Spider):
    name = 'ya_market'
    allowed_domains = ['asos.com']
    start_urls = ['https://www.asos.com/ru/converse/svetlye-vysokie-kedy-converse-run-star-hike/prd/201692322?clr=belyj&colourWayId=201692324&cid=26090']  # TODO: Maybe https

    def parse(self, response):
        # self.log("title: %s" % response.xpath('//*[@itemprop="name"][1]/text()').extract())
        # self.log("price: %s" % response.xpath('//*[@itemprop="price"][1]/text()').re('[.0-9]+'))
        # self.log("description: %s" % response.xpath('//*[@itemprop="description"][1]/text()').extract())
        # self.log("address: %s" % response.xpath(
        #     '//*[@itemtype="http://schema.org/''Place"][1]/text()'
        # ).extract())
        #
        # self.log("image_urls: %s" % response.xpath(
        #     '//*[@itemprop="image"][1]/@src'
        # ).extract())

        item = AppItem()
        item['title'] = response.css("span.current-price") # response.xpath('//*[@itemprop="name"][1]/text()').extract()
        item['price'] = response.xpath(
            '//*[@itemprop="price"][1]/text()').re('[.0-9]+')
        item['description'] = response.xpath(
            '//*[@itemprop="description"][1]/text()').extract()
        item['address'] = response.xpath(
            '//*[@itemtype="http://schema.org/'
            'Place"][1]/text()').extract()

        item['image_urls'] = response.xpath(
            '//*[@itemprop="image"][1]/@src').extract()

        return item

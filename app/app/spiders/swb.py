import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from app.items import OzonProductItem


class SwbSpider(scrapy.Spider):
    name = 'swb'
    allowed_domains = ['www.wildberries.ru']

    # start_urls = ['http://https://www.wildberries.ru/']

    def start_requests(self):
        urls = ['https://www.wildberries.ru/catalog/zhenshchinam',
                'https://www.wildberries.ru/catalog/obuv',
                'https://www.wildberries.ru/catalog/detyam',
                'https://www.wildberries.ru/catalog/muzhchinam',
                'https://www.wildberries.ru/catalog/dom-i-dacha',
                'https://www.wildberries.ru/catalog/krasota',
                'https://www.wildberries.ru/catalog/aksessuary',
                'https://www.wildberries.ru/catalog/elektronika',
                'https://www.wildberries.ru/catalog/igrushki',
                'https://www.wildberries.ru/catalog/aksessuary/tovary-dlya-vzroslyh',
                'https://www.wildberries.ru/catalog/pitanie',
                'https://www.wildberries.ru/catalog/bytovaya-tehnika',
                'https://www.wildberries.ru/catalog/tovary-dlya-zhivotnyh',
                'https://www.wildberries.ru/catalog/aksessuary/avtotovary',
                'https://www.wildberries.ru/catalog/knigi',
                'https://www.wildberries.ru/catalog/yuvelirnye-ukrasheniya',
                'https://www.wildberries.ru/catalog/dom-i-dacha/instrumenty',
                'https://www.wildberries.ru/catalog/dachniy-sezon',
                'https://www.wildberries.ru/catalog/produkty/alkogolnaya-produktsiya',
                'https://www.wildberries.ru/catalog/dom-i-dacha/zdorove',
                'https://www.wildberries.ru/catalog/knigi-i-diski/kantstovary']
        for url in urls:
            yield SeleniumRequest(url=url,
                                  callback=self.parse, wait_time=3600,
                                  wait_until=EC.presence_of_element_located((By.CLASS_NAME, "pagination-next")),
                                  script="window.scrollTo(0, document.body.scrollHeight);")

    def parse(self, response):
        print(response.text)
        for link in LinkExtractor(restrict_css=['div.product-card-list'],
                                  allow=['https://www.wildberries.ru/catalog/[0-9]+/.+']).extract_links(response):
            print(f'link_to: {link.url}')
            yield SeleniumRequest(url=link.url,
                                  callback=self.parse_product,
                                  wait_time=3600,
                                  wait_until=EC.presence_of_element_located((By.CLASS_NAME, "details")),
                                  script="window.scrollTo(0, document.body.scrollHeight);")
        next_page = response.xpath('//a[@class="pagination-next pagination__next"]/@href').get()
        if next_page is not None:
            yield SeleniumRequest(url=next_page,
                                  callback=self.parse, wait_time=3600,
                                  wait_until=EC.presence_of_element_located((By.CLASS_NAME, "pagination-next")),
                                  script="window.scrollTo(0, document.body.scrollHeight);")

    def parse_product(self, response):
        item = OzonProductItem()
        prod = response.css('div.main__container')
        price = prod.css('span.price-block__final-price::text').get()
        if price is not None:
            price = price.replace('\u00a0', '').replace('\u20bd', '').strip()
        item['link'] = response.url
        item['brand'] = prod.css('h1.same-part-kt__header').css('span::text').getall()[0]
        item['title'] = prod.css('h1.same-part-kt__header').css('span::text').getall()[1]
        item['price'] = price
        if prod.xpath('//a[@class="seller-details__title seller-details__title--link"]'
                      '/@href').get() is not None:
            item['sellerID'] = prod.xpath('//a[@class="seller-details__title seller-details__title--link"]'
                                          '/@href').get()
            item['sellerName'] = prod.xpath('//a[@class="seller-details__title seller-details__title--link"]'
                                            '/text()').get()
        elif prod.xpath('//span[@class="seller__name seller__name--short"]/text()').get() is not None:
            item['sellerID'] = prod.xpath('//span[@class="seller__name seller__name--short"]'
                                          '/text()').get()
            item['sellerName'] = prod.xpath('//span[@class="seller__name seller__name--short"]'
                                            '/text()').get()
        item['image'] = response.xpath('//img[@class="photo-zoom__preview j-zoom-preview"]'
                                       '/@src').get()
        params = prod.css('div.product-params')
        first_params = params.css('span.product-params__cell-decor').css('span::text').getall()
        second_params = params.css('td.product-params__cell::text').getall()
        desc = ""
        for i in range(min(len(first_params), len(second_params))):
            desc += f'{item[first_params[i]]}: {second_params[i]}\n'
        item['desc'] = desc
        yield item

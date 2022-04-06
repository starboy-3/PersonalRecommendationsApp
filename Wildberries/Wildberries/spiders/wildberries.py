import scrapy


class WildberriesSpider(scrapy.Spider):
    name = 'wb'
    allowed_domains = ['www.wildberries.ru']
    start_urls = ['https://www.wildberries.ru/catalog/elektronika/noutbuki-periferiya/kompyutery?page=1']

    def parse(self, response):
        for product in response.css('div.j-card-item'):
            link_to_product = product.css('a.j-open-full-product-card::attr(href)').get()
            yield response.follow(link_to_product, callback=self.parse_product)
        
        next_page = response.css('a.pagination__next').attrib['href']
        if next_page != None:
            yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response):
        product = response.css('div.main__container')

        for prod in product:
            price = prod.css('span.price-block__final-price::text').get()
            if price != None:
                price = price.replace('\u00a0', '').replace('\u20bd', '').strip()
            item = dict()
            item['Ссылка'] = response.url
            item['Бренд'] = prod.css('h1.same-part-kt__header').css('span::text').getall()[0]
            item['Название'] = prod.css('h1.same-part-kt__header').css('span::text').getall()[1]
            item['Цена'] = price
            # item['id продавца'] = prod.css('a.seller-details__title').attrib['href'].split('/')[-1]
            print(prod.get()[prod.get().find('seller') - 15 : prod.get().find('seller') + 15])
            print(prod.css('div.same-part-kt__seller-wrap').getall())
            params = prod.css('div.product-params')
            first_params = params.css('span.product-params__cell-decor').css('span::text').getall()
            second_params = params.css('td.product-params__cell::text').getall()
            for i in range(len(first_params)):
                item[first_params[i]] = second_params[i]

            yield item

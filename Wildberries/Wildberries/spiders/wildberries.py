import scrapy


class WildberriesSpider(scrapy.Spider):
    name = 'wb'
    allowed_domains = ['www.wildberries.ru']
    start_urls = [
        # 'https://www.wildberries.ru/catalog/yuvelirnye-ukrasheniya/koltsa',     # FOR RUN IN TEST MODE
        'https://www.wildberries.ru/catalog/zhenshchinam',
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
        'https://www.wildberries.ru/catalog/knigi-i-diski/kantstovary'
    ]

    def parse(self, response):
        list = response.css('div.menu-catalog').css('ul.menu-catalog__list-2').css('li')
        print(list.css('a::attr(href)').getall())
        for cat in list:
            link_to_cat = cat.css('a::attr(href)').get()
            link_to_cat = link_to_cat + '?page=1'
            yield response.follow(link_to_cat, callback=self.parse_page)

    def parse_page(self, response):
        for product in response.css('div.j-card-item'):
            link_to_product = product.css('a.j-open-full-product-card::attr(href)').get()
            yield response.follow(link_to_product, callback=self.parse_product)

        next_page = response.css('a.pagination__next').attrib['href']
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response):
        product = response.css('div.main__container')

        for prod in product:
            price = prod.css('span.price-block__final-price::text').get()
            if price is not None:
                price = price.replace('\u00a0', '').replace('\u20bd', '').strip()
            item = dict()
            item['Ссылка'] = response.url
            item['Бренд'] = prod.css('h1.same-part-kt__header').css('span::text').getall()[0]
            item['Название'] = prod.css('h1.same-part-kt__header').css('span::text').getall()[1]
            item['Цена'] = price
            item['id продавца'] = response.xpath('//div[@class = "seller-details__logo-wrap"]/a/@href', re=r'\d+').get()
            # item['Категория'] = response.xpath('//*[@id="container"]/div[1]/div[1]/div').css('ul').css('li')[
            # -2].css('a').css('span::text').get()
            params = prod.css('div.product-params')
            first_params = params.css('span.product-params__cell-decor').css('span::text').getall()
            second_params = params.css('td.product-params__cell::text').getall()
            desc = ''
            for i in range(len(first_params)):
                desc += str(first_params[i]) + ':' + str(second_params[i]) + '\n'
            item['Описание'] = desc
            yield item

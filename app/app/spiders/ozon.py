import scrapy
import json


class OzonSpider(scrapy.Spider):
    name = 'ozon'
    allowed_domains = ['ozon.ru']
    start_urls = ['https://www.ozon.ru/api/composer-api.bx/_action/v2/categoryChildV2?menuId=1&categoryId=15500&hash=bfe77051-7cd6-456f-97e9-3df232db3e36']
    custom_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 5.0,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0
    }

    def parse(self, response):
        def get_json_page(s):
            return f'https://www.ozon.ru/api/composer-api.bx/page/json/v2?url={s}'
        data = json.loads(response.text)
        categories = data['data']['categories']
        for cat in categories:
            for c in cat['categories']:
                yield scrapy.Request(get_json_page(c['url']), self.parse_cat)


    def parse_cat(self, response):
        def get_json_page(s):
            return f'https://www.ozon.ru/api/composer-api.bx/page/json/v2?url={s}'

        self.logger.info('Parse function called on %s', response.url)

        data = json.loads(response.text)
        widgetStates = data['widgetStates']
        nextpage = None
        if 'nextPage' in data:
            nextpage = data['nextPage']
        for key, val in widgetStates.items():
            val = json.loads(val)
            if 'megaPaginator' in key:
                if 'nextPage' in val and nextpage is None:
                    nextpage = val['nextPage']
            if 'searchResultsV2' in key:
                for i in val['items']:
                    if 'link' in i['action']:
                        yield scrapy.Request(get_json_page(i['action']['link']), self.parse_product)

        if nextpage is not None:
            yield scrapy.Request(get_json_page(nextpage), self.parse_cat)

    def parse_product(self, response):
        self.logger.info('Parse Product function called on %s', response.url)
        data = json.loads(response.text)
        widgetStates = data['widgetStates']
        item = {}
        lti = json.loads(data['layoutTrackingInfo'])
        if 'brandName' in lti:
            item['Brand'] = lti['brandName']
        if 'categoryName' in lti:
            item['Category'] = lti['categoryName']
        item['Link'] = 'https://www.ozon.ru' + response.url.split('=')[1].split('?')[0]
        desc = ''
        for key, val in widgetStates.items():
            val = json.loads(val)
            if 'webProductHeading' in key:
                if 'title' in val:
                    item['Название'] = val['title']
            if 'webSale' in key:
                if 'price' in val['offers'][0]:
                    item['Price'] = val['offers'][0]['price']
                    item['Price'] = item['Price'].replace('\u2009', '').replace('₽', '')
            if 'webCurrentSeller' in key:
                if 'id' in val:
                    item['sellerID'] = val['id']
                if 'name' in val:
                    item['SellerName'] = val['name']
            if 'webGallery' in key:
                if 'coverImage' in val:
                    item['Image'] = val['coverImage']
                else:
                    item['Image'] = 'Изображение отсутствует'
            if 'webCharacteristics' in key:
                if 'characteristics' in val:
                    chars = val['characteristics']
                    for k in chars[0]['short']:
                        desc += k['name'] + ' : '
                        b = False
                        for j in k['values']:
                            if b:
                                desc += ', '
                            b = True
                            desc += j['text']
                        desc += '\n'
                item['Desc'] = desc
        if item['Price'] == '':
            fd = open('jsons/' + item['Название'], 'w')
            fd.write(response.text)
            fd.close()
            yield scrapy.Request(response.url, self.parse_product)

        yield item

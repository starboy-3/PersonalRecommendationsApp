import scrapy
import json

from app.items import OzonProductItem


class OzonSpider(scrapy.Spider):
    name = 'ozon'
    allowed_domains = ['ozon.ru']

    def start_requests(self):
        url = 'https://www.ozon.    ru/api/composer-api.bx/_action/v2/categoryChildV2?menuId=1&categoryId=15500'
        yield scrapy.Request(url)

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
        item = OzonProductItem()
        lti = json.loads(data['layoutTrackingInfo'])
        if 'brandName' in lti:
            item['brand'] = lti['brandName']
        if 'categoryName' in lti:
            item['category'] = lti['categoryName']
        item['link'] = 'https://www.ozon.ru' + response.url.split('=')[1].split('?')[0]
        desc = ''
        for key, val in widgetStates.items():
            val = json.loads(val)
            if 'webProductHeading' in key:
                if 'title' in val:
                    item['title'] = val['title']
            if 'webSale' in key:
                if 'price' in val['offers'][0]:
                    item['price'] = val['offers'][0]['price']
                    item['price'] = item['price'].replace('\u2009', '').replace('₽', '')
            if 'webCurrentSeller' in key:
                if 'id' in val:
                    item['sellerID'] = val['id']
                if 'name' in val:
                    item['sellerName'] = val['name']
            if 'webGallery' in key:
                if 'coverImage' in val:
                    item['image'] = val['coverImage']
                else:
                    item['image'] = 'Изображение отсутствует'
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
                item['desc'] = desc
        if item['price'] == '':
            fd = open('jsons/' + item['Название'], 'w')
            fd.write(response.text)
            fd.close()
            yield scrapy.Request(response.url, self.parse_product)

        yield item

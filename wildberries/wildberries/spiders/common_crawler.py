import re

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector

from wildberries.items import PageItem, PageItemLoader, ProductItem, ProductItemLoader


def remove_params(link: str) -> str:
    if len(link.split('?')) == 1:
        return link
    return link[:link.rfind('?')]


def remove_params_except_page(link: str) -> str:
    if len(link.split('?')) == 1:
        return link
    query_i = link.rfind('?')
    params = link[query_i + 1:]
    result_p = re.findall(r'page=[0-9]+', params)
    if result_p:
        return link[:query_i + 1] + result_p[0]
    return link[:query_i]


class CommonCrawler(CrawlSpider):
    name = 'common_crawler'
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
    rules = [
        Rule(   # parse all category links
            LinkExtractor(
                deny_extensions=['aspx', 'axd'],
                allow='https://www.wildberries.ru/catalog/.+',
                deny=['.*/catalog/premium/.*',
                      '.*catalog/sport/.*',
                      '.*/catalog/[0-9]+/.*',
                      '.*/services/.*',
                      '.*/catalog/vybor-pokupateley/.*'],
                process_value=remove_params
            ),
            callback='parse_page',
            follow=True
        ),
        Rule(   # parse pagination
            LinkExtractor(
                    restrict_css=['#catalog div.pager-bottom a.pagination__next'],
                    allow=[r'https://www.wildberries.ru/catalog/.+\?page=[0-9]+'],  # [0-9]$ FOR RUN IN TEST MODE
                    process_value=remove_params_except_page
            ),
            follow=True     # we should search for products in this page
        ),
        Rule(   # parse product
            LinkExtractor(
                restrict_css=['div.product-card-list'],
                allow=['https://www.wildberries.ru/catalog/[0-9]+/.+'],
                process_value=remove_params_except_page
            ),
            callback='parse_product',
            follow=False
        )
    ]

    @staticmethod
    def parse_page(response):
        selector = Selector(response)
        loader = PageItemLoader(PageItem(), selector)
        loader.add_value('url', response.url)
        path_css_selector = "div.breadcrumbs__container ul.breadcrumbs__list li.breadcrumbs__item " \
                            "span[itemprop='name']::text"
        loader.add_value('path', '/'.join(map(
                lambda s: s.get(),
                response.css(path_css_selector)
        )))
        return loader.load_item()

    @staticmethod
    def parse_product(response):
        selector = Selector(response)
        loader = ProductItemLoader(ProductItem(), selector)
        loader.add_value('product_id', re.search('.*/([0-9]+)/.*', response.url, re.IGNORECASE).group(1))
        loader.add_xpath('product_name', '//span[contains(@data-link, "text{:product^goodsName}")]/text()')
        loader.add_xpath('seller', '//span[contains(@data-link, "text{:product^brandName}")]/text()')
        loader.add_css('price', 'div.same-part-kt__price-block > div > div > '
                                'p.price-block__price-wrap > span.price-block__final-price::text')
        loader.add_css('description', '#container > div.product-detail__section-wrap > '
                                      'div.product-detail__details-wrap > section:nth-child(3) > '
                                      'div:nth-child(2) > div.collapsable__content.j-description > p::text')
        return loader.load_item()

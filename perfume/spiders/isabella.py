import numpy as np
import requests
import lxml.html
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
from perfume.items import PerfumeItem

class IsabellaSpider(CrawlSpider):
    name = 'isabella'
    allowed_domains = ['isolee.com']
    start_urls = ['https://isolee.com/es/']
    sesh = requests.Session()
    script = """
    var result;
    jQuery.ajaxSetup({{async: false}});
    jQuery.getJSON('{}', (data)=>{{result=data;}});
    result;
    """
    le_cat = LinkExtractor(restrict_css='div.buttonnew > a')

    le_start=LinkExtractor(restrict_xpaths=
                           '//ul[@class="nav navbar-nav megamenu horizontal"]/li[1]/a')
    rules = (
        Rule(le_start, callback='parse_cat_page', follow=False),
    )

    def parse_cat_page(self, response):
        for link in self.le_cat.extract_links(response):
            yield SplashRequest(link.url, endpoint='render.json', callback=self.parse_page,
                                args={'js_source': self.script.format(link.url), 'wait': 15, 'script': 1, 'timeout': 400, 'session_id': 'foo',
                                      'headers': {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'}})

    def parse_page(self, response):
        pagination_dict = response.data['script']['pagination']
        loader = ItemLoader(item=PerfumeItem(), response=response)
        for i in range(len(response.data['script']['products'])):
            prod_dict = dict(response.data['script']['products'][i])
            loader.add_value('brand', prod_dict['manufacturer_name'])
            loader.add_value('name_var', prod_dict['name'])
            loader.add_value('price_eu', prod_dict['price_amount'])
            r = self.sesh.get(prod_dict['url'], headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'})
            parser = lxml.html.fromstring(r.content)
            ean = parser.xpath('//div[@style="display:none;"]/span/text()')
            if ean!=[]:
                ean = str(ean[0])
                loader.add_value('ean', ean)
            else:
                loader.add_value('ean', np.nan)
        yield loader.load_item()
        if pagination_dict['current_page'] < pagination_dict['pages_count']:
            if isinstance(pagination_dict['pages'], dict):
                keys_list = list(pagination_dict['pages'].keys())
                yield SplashRequest(pagination_dict['pages'][keys_list[-1]]['url'], endpoint='render.json', callback=self.parse_page,
                                args={'js_source': self.script.format(pagination_dict['pages'][keys_list[-1]]['url']), 'script': 1, 'wait': 15, 'timeout': 400, 'session_id': 'foo',
                                     'headers': {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'}})
            else:
                yield SplashRequest(pagination_dict['pages'][-1]['url'], endpoint='render.json',
                                    callback=self.parse_page,
                                    args={
                                        'js_source': self.script.format(pagination_dict['pages'][-1]['url']),
                                        'script': 1, 'wait': 15, 'timeout': 400, 'session_id': 'foo',
                                        'headers': {
                                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'}})
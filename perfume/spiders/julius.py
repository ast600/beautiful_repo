import requests
from w3lib.http import basic_auth_header
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.exceptions import CloseSpider
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
from perfume.items import PerfumeItem


class JuliusSpider(CrawlSpider):
    name = 'julius'
    allowed_domains = ['perfumeriajulia.es']
    start_urls = ['https://www.perfumeriajulia.es/']
    sesh = requests.Session()
    le_item = LinkExtractor(restrict_css='h2.product-title > a')
    custom_settings = {'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'}
    lua_scroll = """
    function main(splash, args)
        splash.images_enabled=false
        splash.resource_timeout=10.0
        splash:on_request(function(request)
            request:set_header('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36')
            request:set_header('accept', '*/*')
            request:set_header('accept-language', 'es-ES')
        end)
        splash:go(args.url)
        splash:wait(2)
        local len = splash:evaljs("document.querySelectorAll('button.loadMore.next.hidden').length;")
        local totalItems=splash:evaljs("parseInt(document.querySelector('span.af-total-count').innerText);")
        while len==0
            do
            splash:runjs("$('button.loadMore.next').click();")
            splash:wait(1)
            len=splash:evaljs("document.querySelectorAll('button.loadMore.next.hidden').length;")
        end
        splash:wait(1)
    return 
    {html = splash:html(),
    items = totalItems}
    end"""
    lua_item = """
        function main(splash, args)
        splash.images_enabled=false
        splash.resource_timeout=10.0
        splash:on_request(function(request)
            request:set_header('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36')
            request:set_header('accept', '*/*')
            request:set_header('accept-language', 'es-ES')
        end)
        splash:go(args.url)
        splash:wait(5)
        local itemArr=splash:evaljs([[try {
            let lilialVar;
            document.querySelectorAll('div#collapse-product-ingredients > div > p').length > 0 ? lilialVar=/lilial|butylphenyl methylpropional/i.test(document.querySelectorAll('div#collapse-product-ingredients > div > p')[0].innerText) : lilialVar='N/A';
            let spfVar;
            document.querySelectorAll('div#collapse-product-ingredients > div > p').length > 0 ? spfVar=/spf/i.test(document.querySelectorAll('div#collapse-product-ingredients > div > p')[0].innerText) || /spf/i.test(document.querySelector('h1').innerText) : spfVar=/spf/i.test(document.querySelector('h1').innerText);
            let jsonArr=Array.from(document.querySelectorAll('script[type="application/ld+json"]')).map(elem => JSON.parse(elem.innerText.replace(/\\n/gi, ''))).filter(elem => elem['@type']=='Product')[0];
            let matchAsArr={sku: jsonArr.sku, ean: jsonArr.gtin13}
            let strArr=idsProducts.map(elem => elem.toString());
            let resArr={keyArray: matchAsArr, prodArray: strArr, partnerId: rrPartnerId, spf: spfVar, lilial: lilialVar};
            resArr;
            }
        catch(err) {
            let resArr=undefined; resArr;
            }]])
        return itemArr
        end"""

    le_start = LinkExtractor(restrict_css='ul#menu>li:not(:nth-child(1)):not(:nth-child(10)):not(:nth-child(9)):not(:nth-child(8)) >a')
    rule_start = Rule(le_start, callback='scroll_page', follow=False)

    rules = (
        rule_start,
    )

    def scroll_page(self, response):
        yield SplashRequest(response.url, endpoint='execute', callback=self.splash_item,
                            args={'lua_source': self.lua_scroll, 'timeout': 800, 'session_id': 'gnu'}, splash_headers={'Authorization': basic_auth_header('admin', 'admin')})

    def splash_item(self, response):
        if response.data['items'] >= len(self.le_item.extract_links(response)):
            for link in self.le_item.extract_links(response):
                yield SplashRequest(link.url, endpoint='execute', callback=self.parse_item, args={'lua_source': self.lua_item,
                                                                                                  'timeout': 800, 'session_id': 'gnu'}, splash_headers={'Authorization': basic_auth_header('admin', 'admin')})
        else:
            raise CloseSpider(reason=f"Only {len(self.le_item.extract_links(response))} out of {response.data['items']} were selected")

    def parse_item(self, response):
        if hasattr(response, 'data'):
            base_url = 'https://api.retailrocket.net/api/1.0/partner/{0}/items/?itemsIds={1}'
            r = self.sesh.get(base_url.format(response.data['partnerId'], ','.join(response.data['prodArray'])))
            r_json = r.json()
            r_clean = [r_json[i] for i in range(len(r_json)) if str(r_json[i]['ItemId']) in response.data['keyArray']['sku']]
            if len(r_clean)>0 and r_clean[0]['Vendor'] is not None and 'ean' in response.data['keyArray'].keys():
                prod_dict = {'brand': r_clean[0]['Vendor'], 'name_var': r_clean[0]['Name'], 'ean': response.data['keyArray']['ean'], 'price_eu': r_clean[0]['Price'], 'url': r_clean[0]['Url']}
                loader = ItemLoader(item=PerfumeItem(), response=response)
                loader.add_value('brand', prod_dict['brand'])
                loader.add_value('name_var', prod_dict['name_var'])
                loader.add_value('ean', prod_dict['ean'])
                loader.add_value('spf', response.data['spf'])
                loader.add_value('lilial', response.data['lilial'])
                loader.add_value('price_eu', prod_dict['price_eu'])
                loader.add_value('url', prod_dict['url'])
                yield loader.load_item()
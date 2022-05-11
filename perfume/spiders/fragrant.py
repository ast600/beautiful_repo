import numpy as np
import scrapy
from scrapy.shell import inspect_response
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
from perfume.items import PerfumeItem


class FragrantSpider(CrawlSpider):
    name = 'fragrant'
    allowed_domains = ['perfumesclub.com']
    start_urls = ['https://www.perfumesclub.com/']
    link_ex = LinkExtractor(restrict_xpaths=
                               '//div[@id="ajaxPage"]/div/div[@class="pInfo"]/div[@class="contpInfo"]/a[2]')
    lua = '''
        function main(splash, args)
            splash:go(args.url)
            splash:wait(1)
            repeat
                splash:runjs("$('div#NewPage > a').click();")
                splash:wait(3)
                local len = splash:evaljs('document.querySelectorAll("div#NewPage").length;')
            until (len==0)
            local items=splash:evaljs("filter.GetModel().totalItems;")  
        return {items=items, html=splash:html()}
        end
        '''

    le_start = LinkExtractor(restrict_xpaths=
                             '//div[@class="new-menu-level-2 col-12 toolbarBelleza"]//div[@class="mainLink"][1]/a')

    rule_start = Rule(le_start, callback='splash_scroll', follow=False)

    rules = (rule_start,)

    def splash_scroll(self, response):
        return SplashRequest(response.url, callback=self.splash_parse, endpoint='execute', args={'lua_source': self.lua,
                                                                                                 'timeout': 400})

    def splash_parse(self, response):
        if response.data['items'] == len(self.link_ex.extract_links(response)):
            self.logger.info(f"All {len(self.link_ex.extract_links(response))} items are selected! Let's cROLL!")
            for link in self.link_ex.extract_links(response):
                yield scrapy.Request(link.url, callback=self.parse_item)
        else:
            raise CloseSpider(reason=
                              f'Not all items are selected (Only {len(self.link_ex.extract_links(response))} out of {response.data["items"]}).')

    def parse_item(self, response):
        loader = ItemLoader(item=PerfumeItem(), response=response)
        loader.add_xpath('brand', '//h1/a/text()')
        loader.add_xpath('name', '//h1/span/text()')
        loader.add_xpath('volume', '//div[@class="font-16 font-w-700 tM1"]/text()')
        loader.add_xpath('price_eu', '//div[@class="col-12"]//div[@class="contPrecioNuevo"]/text()')
        loader.add_xpath('ean', '//dt[contains(., "EAN")]/following-sibling::dd/text()')
        return loader.load_item()

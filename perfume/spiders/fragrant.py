import scrapy
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
    lua_scroll = '''
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
    lua_item = '''
    function main(splash, args)
        splash:go(args.url)
        local dic = splash:evaljs("productList;")
    return {dic=dic, html=splash:html()}
    end
    '''

    le_start = LinkExtractor(restrict_xpaths=
                             '//div[@class="new-menu-level-2 col-12 toolbarBelleza"]//div[@class="mainLink"][1]/a')

    rule_start = Rule(le_start, callback='splash_scroll', follow=False)

    rules = (rule_start,)

    def splash_scroll(self, response):
        return SplashRequest(response.url, callback=self.splash_parse, endpoint='execute',
                             args={'lua_source': self.lua_scroll, 'timeout': 400})

    def splash_parse(self, response):
        if response.data['items'] == len(self.link_ex.extract_links(response)):
            self.logger.info(f"All {len(self.link_ex.extract_links(response))} items are selected! Let's cROLL!")
            for link in self.link_ex.extract_links(response):
                yield SplashRequest(link.url, callback=self.parse_item, endpoint='execute',
                                    args={'lua_source': self.lua_item})
        else:
            raise CloseSpider(reason=
                              f'Not all items are selected (Only {len(self.link_ex.extract_links(response))} out of {response.data["items"]}).')

    def parse_item(self, response):
        perf_item = PerfumeItem()
        loader = ItemLoader(item=perf_item, response=response)
        for key in response.data['dic'].keys():
            loader.add_value('brand', response.data['dic'][key]['brand'])
            loader.add_value('name_var', response.data['dic'][key]['name']+','+response.data['dic'][key]['variant'])
            loader.add_value('price_eu', response.data['dic'][key]['price'])
        loader.add_xpath('ean', '//dt[contains(., "EAN")]/following-sibling::dd/text()')
        yield loader.load_item()

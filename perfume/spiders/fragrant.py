from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
import repackage

repackage.up(2)

from perfume.items import PerfumeItem


class FragrantSpider(CrawlSpider):
    name = 'fragrant'
    allowed_domains = ['perfumesclub.pt']
    start_urls = ['https://www.perfumesclub.pt']
    le_item = LinkExtractor(restrict_xpaths=
                            '//div[@id="ajaxPage"]/div/div[@class="pInfo"]/div[@class="contpInfo"]/a[2]')
    lua_scroll = '''
    function main(splash, args)
        splash.images_enabled=false
        splash.resource_timeout=30.0
        splash:on_request(function(request)
            request:set_header('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36')
            request:set_header('accept', '*/*')
        end)
        splash:go(args.url)
        splash:wait(10)
        local total=splash:evaljs("filter.GetModel().totalItems;")
        local perPage=splash:evaljs("filter.GetModel().itemsPorPagina;")
  		local items=splash:evaljs("filter.GetModel().totalItems;")
  		local pages = math.ceil(total/perPage)
        splash:runjs(string.format("window.location.search=\'pagina=%d\';", pages))
        splash:wait(180)
    return {items=items, html=splash:html()}
    end
    '''
    lua_item = '''
    function main(splash, args)
        splash.images_enabled=false
        splash:go(args.url)
        splash:wait(3)
        local itemArr=splash:evaljs([[
            function getEan() {if ($("dt:contains('EAN')").length>0) {let prodLen=Object.keys(productList).length;
                let cleanArr=$("dt:contains('EAN')")[0].nextElementSibling.childNodes[0].data.trim().replace(/\s/g, '').replace('/...','').split('/');
                    if (cleanArr.length==prodLen) {return cleanArr;}
                    else {while (cleanArr.length<prodLen) {cleanArr.push("Not found")}; return cleanArr;}}
                else {let newArr=[]; while (newArr.length<Object.keys(productList).length) {newArr.push('Not found')}; return newArr;}}
        let eanArr=getEan();
        let ind=0;
        let copyAsArr=productList;
        for (let key of Object.keys(copyAsArr)) {copyAsArr[key]['url']=window.location.href;
            copyAsArr[key]['ean']=eanArr[ind]; ind++};
        copyAsArr;]])
        return itemArr
        end
        '''

    le_start = LinkExtractor(restrict_xpaths=
                             '//div[@class="new-menu-level-2 col-12 toolbarBelleza"]//div[@class="mainLink"]/a')

    rule_start = Rule(le_start, callback='splash_scroll', follow=False)

    rules = (rule_start,)

    def splash_scroll(self, response):
        return SplashRequest(response.url, callback=self.splash_parse, endpoint='execute',
                             args={'lua_source': self.lua_scroll, 'timeout': 800})

    def splash_parse(self, response):
        if response.data['items'] == len(self.le_item.extract_links(response)):
            self.logger.info(f"All {len(self.le_item.extract_links(response))} items are selected! Let's cROLL!")
            for link in self.le_item.extract_links(response):
                yield SplashRequest(link.url, callback=self.parse_item, endpoint='execute',
                                    args={'lua_source': self.lua_item, 'timeout': 800})
        else:
            raise CloseSpider(reason=
                              f'Not all items are selected (Only {len(self.le_item.extract_links(response))} out of {response.data["items"]}).')

    def parse_item(self, response):
        for key in response.data.keys():
            loader = ItemLoader(item=PerfumeItem(), response=response)
            loader.add_value('brand', response.data[key]['brand'])
            loader.add_value('name_var',
                             response.data[key]['name'] + ',' + response.data[key]['variant'])
            if len(list(response.data.keys())) > 1:
                loader.add_value('ean', response.data[key]['ean'] + '[!]')
            else:
                loader.add_value('ean', response.data[key]['ean'])
            loader.add_value('price_eu', response.data[key]['price'])
            loader.add_value('url', response.data[key]['url'])
            yield loader.load_item()


class ComFragrantSpider(FragrantSpider):
    name = 'com_fragrant'
    allowed_domains = ['perfumesclub.com']
    start_urls = ['https://www.perfumesclub.com']

if __name__ == '__main__':

    from twisted.internet import reactor, defer

    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)

    @defer.inlineCallbacks
    def crawl():
        yield runner.crawl(FragrantSpider)
        yield runner.crawl(ComFragrantSpider)
        reactor.stop()

    crawl()
    reactor.run()
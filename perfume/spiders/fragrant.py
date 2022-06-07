from scrapy.exceptions import CloseSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
from perfume.items import PerfumeItem


class FragrantSpider(CrawlSpider):
    name = 'fragrant'
    allowed_domains = ['perfumesclub.pt']
    start_urls = ['https://www.perfumesclub.pt/']
    le_item = LinkExtractor(restrict_xpaths=
                            '//div[@id="ajaxPage"]/div/div[@class="pInfo"]/div[@class="contpInfo"]/a[2]')
    lua_scroll = '''
    function main(splash, args)
        splash:go(args.url)
        splash:wait(4)
        local total=splash:evaljs("filter.GetModel().totalItems;")
        local perPage=splash:evaljs("filter.GetModel().itemsPorPagina;")
  		local items=splash:evaljs("filter.GetModel().totalItems;")
  		local pages = math.ceil(total/perPage)
        splash:runjs(string.format("window.location.search=\'pagina=%d\';", pages))
        splash:wait(100)
    return {items=items, html=splash:html()}
    end
    '''
    js_item = '''
    function checkLilial() {
        let resVar; let textVar = document.querySelectorAll('div.description[itemprop="characteristics"]')[0].innerText;
        let regexIng = /ingredientes/i; let regexLil = /Lilial|butylphenyl methylpropional/i;
        regexIng.test(textVar)==true ? resVar=regexLil.test(textVar) : resVar="N/A"; return resVar;}
    let lilValue= document.querySelectorAll('div.description[itemprop="characteristics"]')>0 ? checkLilial() : "N/A";

    function getEan() {
    if ($("dt:contains('EAN')").length>0)
    {let prodLen=Object.keys(productList).length;
    let cleanArr=$("dt:contains('EAN')")[0].nextElementSibling.childNodes[0].data.trim().replace(/\s/g, '').replace('/...','').split('/');
        if (cleanArr.length==prodLen) {return cleanArr;}
        else {while (cleanArr.length<prodLen) {cleanArr.push("Not found")}; return cleanArr;}}
    else {let newArr=[]; while (newArr.length<Object.keys(productList).length) {newArr.push('Not found')}; return newArr;}}
    let eanArr=getEan();
    let ind=0;
    let copyAsArr=productList; let spfRegex=/spf/i
    for (let key of Object.keys(copyAsArr)) {copyAsArr[key]['url']=window.location.href; copyAsArr[key]['lilial']=lilValue;
    copyAsArr[key]['spf']=spfRegex.test(copyAsArr[key].name) || $("dt:contains('SPF')").length>0; copyAsArr[key]['ean']=eanArr[ind]; ind++};
    copyAsArr;
    '''

    le_start = LinkExtractor(restrict_xpaths=
                             '//div[@class="new-menu-level-2 col-12 toolbarBelleza"]//div[@class="mainLink"][1]/a')

    rule_start = Rule(le_start, callback='splash_scroll', follow=False)

    rules = (rule_start,)

    def splash_scroll(self, response):
        return SplashRequest(response.url, callback=self.splash_parse, endpoint='execute',
                             args={'lua_source': self.lua_scroll, 'timeout': 400})

    def splash_parse(self, response):
        if response.data['items'] == len(self.le_item.extract_links(response)):
            self.logger.info(f"All {len(self.le_item.extract_links(response))} items are selected! Let's cROLL!")
            for link in self.le_item.extract_links(response):
                yield SplashRequest(link.url, callback=self.parse_item, endpoint='render.json',
                                    args={'js_source': self.js_item, 'html': 1, 'script': 1, 'wait': 10,
                                          'timeout': 400})
        else:
            raise CloseSpider(reason=
                              f'Not all items are selected (Only {len(self.le_item.extract_links(response))} out of {response.data["items"]}).')

    def parse_item(self, response):
        for key in response.data['script'].keys():
            loader = ItemLoader(item=PerfumeItem(), response=response)
            loader.add_value('brand', response.data['script'][key]['brand'])
            loader.add_value('name_var',
                             response.data['script'][key]['name'] + ',' + response.data['script'][key]['variant'])
            if len(list(response.data['script'].keys())) > 1:
                loader.add_value('ean', response.data['script'][key]['ean'] + '[!]')
            else:
                loader.add_value('ean', response.data['script'][key]['ean'])
            loader.add_value('spf', response.data['script'][key]['spf'])
            loader.add_value('lilial', response.data['script'][key]['lilial'])
            loader.add_value('price_eu', response.data['script'][key]['price'])
            loader.add_value('url', response.data['script'][key]['url'])
            yield loader.load_item()
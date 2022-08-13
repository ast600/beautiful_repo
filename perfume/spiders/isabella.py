from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
from perfume.items import PerfumeItem

class IsabellaSpider(CrawlSpider):
    name = 'isabella'
    allowed_domains = ['isolee.com']
    start_urls = ['https://isolee.com/es/']
    lua_script = """
    function main(splash, args)
        splash.images_enabled=false
        assert(splash:go(args.url))
        assert(splash:wait(10))
        local itemArr = splash:evaljs(string.format([[var result;
            jQuery.ajaxSetup({async: false});
            jQuery.getJSON("%s", (data)=>{result=data;});
            let copyAsArr=[];
            while (copyAsArr.length<result.products.length) {copyAsArr.push({})};
            for (let i=0; i<result.products.length; i++)
                {copyAsArr[i]['brand']=result.products[i].manufacturer_name; copyAsArr[i]['name_var']=result.products[i].name;
                copyAsArr[i]['price_eu']=result.products[i].price_amount;
                copyAsArr[i]['url']=result.products[i].url; jQuery.ajax({async: false, url: result.products[i].url, success:
                (data)=>{let doc=new DOMParser().parseFromString(data, 'text/html'); let ajaxSel=doc.querySelectorAll("div[class='tab-pane fade']");
                copyAsArr[i]['ean']=doc.querySelectorAll("span[itemprop='gtin']")[0].innerText!='' ? doc.querySelectorAll("span[itemprop='gtin']")[0].innerText : "Not found";}})}
            let fullArr={pagination: result.pagination, productData: copyAsArr};
        fullArr;]], args.url))
        return
            itemArr
    end
    """
    
    le_cat = LinkExtractor(restrict_css='div.buttonnew > a')

    le_start=LinkExtractor(restrict_xpaths=
                           '//ul[@class="nav navbar-nav megamenu horizontal"]/li[1]/a')
    rules = (
        Rule(le_start, callback='parse_cat_page', follow=False),
    )

    def parse_cat_page(self, response):
        for link in self.le_cat.extract_links(response):
            yield SplashRequest(link.url, endpoint='execute', callback=self.parse_page,
                                args={'lua_source': self.lua_script, 'timeout': 400, 'session_id': 'foo',
                                      'headers': {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'}})

    def parse_page(self, response):
        pagination_dict = response.data['pagination']
        product_arr = response.data['productData']
        for i in range(len(product_arr)):
            loader = ItemLoader(item=PerfumeItem(), response=response)
            loader.add_value('brand', product_arr[i]['brand'])
            loader.add_value('name_var', product_arr[i]['name_var'])
            loader.add_value('ean', product_arr[i]['ean'])
            loader.add_value('price_eu', product_arr[i]['price_eu'])
            loader.add_value('url', product_arr[i]['url'])
            yield loader.load_item()
        
        if pagination_dict['current_page'] < pagination_dict['pages_count']:
            if isinstance(pagination_dict['pages'], dict):
                keys_list = list(pagination_dict['pages'].keys())
                yield SplashRequest(pagination_dict['pages'][keys_list[-1]]['url'], endpoint='execute', callback=self.parse_page,
                                args={'lua_source': self.lua_script, 'timeout': 400, 'session_id': 'foo',
                                     'headers': {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'}})
            else:
                yield SplashRequest(pagination_dict['pages'][-1]['url'], endpoint='execute',
                                    callback=self.parse_page,
                                    args={
                                        'lua_source': self.lua_script, 'timeout': 400, 'session_id': 'foo',
                                        'headers': {
                                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'}})
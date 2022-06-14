from scrapy.linkextractors import LinkExtractor
from scrapy.shell import inspect_response
from scrapy.spiders import CrawlSpider, Rule
from scrapy_splash import SplashRequest
from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider
from perfume.items import PerfumeItem

class DanSpider(CrawlSpider):
    name = 'dan'
    allowed_domains = ['danaperfumerias.com']
    start_urls = ['http://danaperfumerias.com/']
    custom_settings = {'HTTPCACHE_ENABLED': False}
    le_item = LinkExtractor(restrict_css='h3>a.product-name')
    lua_scroll = """
    function main(splash, args)
        splash.images_enabled=false
        assert(splash:go(args.url))
        assert(splash:wait(0.5))
        local numItems = splash:evaljs([[parseInt(document.querySelector('input#nb_item').value);]])
        splash:runjs([[$('button[class="btn btn-default button exclusive-medium"]').click();]])
        splash:wait(80)
    return {
        html = splash:html(),
        numItems = numItems}
    end"""
    lua_item = """
        function main(splash, args)
        splash.images_enabled=false
        splash:go(args.url)
        splash:wait(1)
        local itemArr=splash:evaljs([[
    		let spfVal;
			let resArr=[];
			for (let elem of Array.from(document.querySelectorAll('section#tab3 > table > tbody > tr')))
				{resArr.push(elem.innerText);}
                spfVal=resArr.map(elem => /spf/i.test(elem)).includes(true) ? true : "N/A";
    
    		let lilialVal = "N/A";
			for (let elem of Array.from(document.querySelectorAll('section#tab3 > table > tbody > tr')))
				{/lilial|butylphenyl methylpropional/i.test(elem.innerText)==true ? lilialVal=true : undefined};

    		let prodArr=
                {brand: document.querySelector('span.productbrand').innerText,
                name: document.querySelector('a.product-name').innerText,
                ean: document.querySelector('meta[name="description"]').attributes.content.nodeValue.match(/[0-9]{10,13}/g)[0],
                price_eu: productPrice,
    			lilial: lilialVal,
    			spf: spfVal,
                url: window.location.href};
            prodArr;]])
        return itemArr
        end"""

    le_start=LinkExtractor(restrict_xpaths="//ul[@id='menu']/li[not (position()=1 or position()=2 or position()=10)]/a")
    rule_start=Rule(le_start, callback='scroll_page', follow=False)

    rules = (rule_start,
             )

    def scroll_page(self, response):
        yield SplashRequest(response.url, callback=self.parse_cat, endpoint='execute', dont_filter=True,
                            args={'lua_source': self.lua_scroll, 'timeout': 400})

    def parse_cat(self, response):
        if response.data['numItems']==len(response.xpath('//h3/a[@class="product-name"]')):
            for link in self.le_item.extract_links(response):
                yield SplashRequest(link.url, endpoint='execute', callback=self.parse_item,
                                    args={'lua_source': self.lua_item, 'timeout': 400})
        else:
            raise CloseSpider(reason=f"""Only {len(response.xpath('//h3/a[@class="product-name"]'))} our of {response.data['numItems']} were selected.""")

    def parse_item(self, response):
        if response.status == 200:
            loader = ItemLoader(item=PerfumeItem(), response=response)
            loader.add_value('brand', response.data['brand'])
            loader.add_value('name_var', response.data['name'])
            loader.add_value('ean', response.data['ean'])
            loader.add_value('spf', response.data['spf'])
            loader.add_value('lilial', response.data['lilial'])
            loader.add_value('price_eu', response.data['price_eu'])
            loader.add_value('url', response.data['url'])
            yield loader.load_item()
        else:
            pass
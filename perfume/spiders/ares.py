import scrapy
import requests
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
from perfume.items import PerfumeItem


class AresSpider(CrawlSpider):
    name = 'ares'
    allowed_domains = ['arenal.com']
    start_urls = ['https://www.arenal.com/']
    le_items = LinkExtractor(restrict_xpaths='//h3/a')
    le_next_page = LinkExtractor(restrict_css='a#pagination-next-page')
    sesh = requests.Session()
    js_script = '''
    let spfVar=document.querySelectorAll('div#tab-1').length>0 ? (/spf/i.test(document.querySelectorAll('div#tab-1')[0].innerText) || /spf/i.test(productObj.name)) : (/spf/i.test(productObj.name)==false ? "N/A" : true);
    let lilVar=document.querySelectorAll('div#tab-1').length>0 ? /lilial|butylphenyl methylpropional/i.test(document.querySelectorAll('div#tab-1')[0].innerText) : "N/A";
    let rocketArr=[];
    if (document.querySelectorAll('div.contenedor-variedad').length>0)
        {for (let i=0; i<document.querySelectorAll('div.contenedor-variedad').length; i++)
            {var rocketVal = document.querySelectorAll('div.contenedor-variedad')[i].attributes['data-variant-ean'].value;
            rocketArr.push(rocketVal);}}
    else
        {for (let j=0; j<document.querySelectorAll('button[class="c-addtocartaction__button js-add-to-cart"]').length; j++)
            {var string=document.querySelectorAll('button[class="c-addtocartaction__button js-add-to-cart"]')[j].attributes.onmousedown.value;
            var regex=/[0-9]+/g; var matchArr=string.match(regex); rocketArr.push(...matchArr);}};
    let dict={"spf": spfVar, "lilial": lilVar, "partnerId": rrPartnerId, "codeArr": rocketArr}; dict;
    '''

    le_start = LinkExtractor(restrict_xpaths='//ul[@class="list"]/li/div/a')
    rule_start = Rule(le_start, callback='parse_page', follow=False)
    rules = (rule_start,)

    def parse_page(self, response):
        for link in self.le_items.extract_links(response):
            yield SplashRequest(link.url, endpoint='render.json', callback=self.send_to_api, args=
                {'js_source': self.js_script, 'console': 1, 'timeout': 400, 'wait': 10, 'script': 1, 'session_id': 'fu',
                 'headers': {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'}})
        if len(self.le_next_page.extract_links(response))!=0:
            yield scrapy.Request(url=self.le_next_page.extract_links(response)[0].url, callback=self.parse_page)

    def send_to_api(self, response):
        base_url = 'https://api.retailrocket.net/api/1.0/partner/{0}/items/?itemsIds={1}'
        if 'script' not in response.data.keys(): pass
        elif 'codeArr' in response.data['script'].keys() and len(response.data['script']['codeArr']) > 0:
            code_arr = response.data['script']['codeArr']
            api_code_str = ','.join(code_arr) if len(code_arr) > 1 else code_arr[0]
            r = self.sesh.get(base_url.format(response.data['script']['partnerId'], api_code_str))
            r_json = r.json()
            for i in range(len(response.data['script']['codeArr'])):
                loader = ItemLoader(item=PerfumeItem(), response=response)
                loader.add_value('brand', r_json[i]['Vendor'])
                if len(code_arr) > 1:
                    loader.add_value('name_var', r_json[i]['Name']+','+r_json[i]['Params']['Volume'])
                else:
                    loader.add_value('name_var', r_json[i]['Name'])
                loader.add_value('ean', r_json[i]['ItemId'])
                loader.add_value('spf', response.data['script']['spf'])
                loader.add_value('lilial', response.data['script']['lilial'])
                loader.add_value('price_eu', r_json[i]['Price'])
                loader.add_value('url', r_json[i]['Url'])
                yield loader.load_item()
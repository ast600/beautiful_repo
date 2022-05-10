import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_splash import SplashRequest


class SmellySpider(CrawlSpider):
    name = 'smelly'
    allowed_domains = ['perfumesclub.com']
    start_urls = ['https://www.perfumesclub.com/es/perfume/f/?pagina={}'.format(i) for i in range(1, 58)]

    le_product = LinkExtractor(restrict_xpaths=
                               '//div[@id="ajaxPage"]/div/div[@class="pInfo"]/div[@class="contpInfo"]/a[2]')

    rule_product = Rule(le_product, callback='parse_item', follow=False)

    rules = (rule_product,)

    def parse_item(self, response):
        prices = []
        volumes = []
        eans = []

        for element in response.xpath('//div[@class="contPrecioNuevo"]/text()').getall():
            clean_element = element.strip().replace('\u20ac', '').strip().replace(',', '.')
            prices.append(float(clean_element))

        for vol in response.xpath('//div[@class="font-16 font-w-700 tM1"]/text()').getall():
            clean_vol = vol.strip()
            volumes.append(clean_vol)

        if response.xpath('//dt[contains(., "EAN")]/following-sibling::dd/text()').get() is None:
            eans.append(None)
        else:
            eans = response.xpath('//dt[contains(., "EAN")]/following-sibling::dd/text()').get().strip().split(' / ')

        item = {}
        item['Title'] = response.xpath('//h1/span/text()').get()
        item['Price (EU)'] = prices
        item['Volume'] = volumes
        item['EAN'] = eans
        return item

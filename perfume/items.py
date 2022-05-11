import scrapy
from itemloaders.processors import MapCompose, Identity

def digits_only(val):
    return float(val.strip().replace('\u20ac', '').strip().replace(',', '.'))


class PerfumeItem(scrapy.Item):
    brand = scrapy.Field(input_processor=MapCompose(str.strip), output_processor=Identity())
    name = scrapy.Field(input_processor=MapCompose(str.strip), output_processor=Identity())
    volume = scrapy.Field(input_processor=MapCompose(str.strip), output_processor=Identity())
    price_eu = scrapy.Field(input_processor=MapCompose(digits_only), output_processor=Identity())
    ean = scrapy.Field(input_processor=MapCompose(str.strip), output_processor=Identity())
